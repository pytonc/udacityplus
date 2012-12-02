import unittest
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
from web.models.Message import Conversation
from web.models import User
from web.tests.testdata import *
from copy import deepcopy


class TestMessages(unittest.TestCase):
    def setUp(self):
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.u1 = User.save(username1, email1, password1)
        self.u2 = User.save(username2, email2, password2)

    def tearDown(self):
        self.testbed.deactivate()

    def testCreateConversation(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
                                        title_plain_text,
                                        content_plain_text)


        conv = c.key.get()
        self.assertEqual(conv.title, title_plain_text, 'new conversation title')
        self.assertEqual(conv.messages[0].content, content_plain_text, 'new conversation message')

    def testAddNewMessage(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
                                        title_plain_text,
                                        content_plain_text)

        m = Conversation.add_new_message(self.u2.username,
                                         content_plain_text2, conv_key=c.key)

#        c.put()

        self.assertEqual(len(c.messages_list), 2, "Length of message list %s != %s" % (len(c.messages_list), 2))

        test_cont = (content_plain_text, content_plain_text2)
        for i, msg in enumerate(c.messages_list):
            newmsg = msg.get()
            self.assertEqual(newmsg.content, test_cont[i], "Message Content")

    def testDeleteConversationWithOwner(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
            title_plain_text,
            content_plain_text)

        m = Conversation.add_new_message(self.u2.username,
            content_plain_text2, conv_key=c.key)

        message_keys = deepcopy(c.messages_list)

#        c.put()

        Conversation.delete_conversation(self.u1.username, key=c.key)

        conv = c.key.get()
        self.assertIsNone(conv, "Conversation is not None")

        for k in message_keys:
            msg = k.get()
            self.assertIsNone(msg, "Message is not None")


    def testDeleteConversationWithoutOwner(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
            title_plain_text,
            content_plain_text)

        m = Conversation.add_new_message(self.u2.username,
            content_plain_text2, conv_key=c.key)

#        c.put()

        Conversation.delete_conversation(self.u2.username, key=c.key)

        conv = c.key.get()
        self.assertIsNotNone(conv, "Conversation is None")
        self.assertEqual(conv.deleted_for, self.u2.username,
            "Conversation not deleted for %s" % self.u2.username)

        for m in conv.messages:
            self.assertEqual(m.deleted_for, self.u2.username,
                "Message not deleted for %s" % self.u2.username)

    def testDeleteOneMessageWithOwner(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
            title_plain_text,
            content_plain_text)

        m = Conversation.add_new_message(self.u2.username,
            content_plain_text2, conv_key=c.key)

        Conversation.add_new_message(self.u1.username,
            content_plain_text, conv_key=c.key)

#        c.put()

        self.assertEqual(len(c.messages_list), 3, "Length of messages list != 3")
        Conversation.delete_message(self.u1.username, c.key.id(), m.key.id())
        self.assertEqual(len(c.messages_list), 2, "Length of messages list != 2 after deletion")

        deleted = m.key.get()
        self.assertIsNone(deleted, "Message was not deleted")

    def testDeleteWithoutOwner(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
            title_plain_text,
            content_plain_text)

        m = Conversation.add_new_message(self.u2.username,
            content_plain_text2, conv_key=c.key)

        Conversation.add_new_message(self.u1.username,
            content_plain_text, conv_key=c.key)

#        c.put()

        self.assertEqual(len(c.messages_list), 3, "Length of messages list != 3")
        Conversation.delete_message(self.u2.username, c.key.id(), m.key.id())
        self.assertEqual(len(c.messages_list), 3, "Length of messages list != 3 after deletion")

        deleted = m.key.get()
        self.assertIsNotNone(deleted, "Message is None")
        self.assertEqual(deleted.deleted_for, self.u2.username, "Deleted for is incorrect")

        for k in c.messages_list:
            msg = k.get()
            if k != deleted.key:
                self.assertIsNone(msg.deleted_for, "deleted_for was not None for a message other than deleted")

    def testDeleteConversationWithOneMsgAndOwner(self):
        c, msg = User.add_new_conversation(self.u1.username, self.u2.username,
            title_plain_text,
            content_plain_text)

        self.assertEqual(len(c.messages_list), 1, "1ength of messages list != 1")

        m = c.messages_list[0]

        Conversation.delete_message(self.u1.username, c.key.id(), m.id())

        conv = c.key.get()
        msg = m.get()

        self.assertIsNone(conv, "Conversation was not deleted")
        self.assertIsNone(msg, "Message was not deleted")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMessages))
    return suite