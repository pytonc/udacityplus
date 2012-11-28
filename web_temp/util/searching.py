from google.appengine.api import search
import logging


def create_user_search_document(username, real_name, avatar_url="/img/defaultavatar.png", doc_id=None):
    """Create a Document that will allow searching for people based on their username and real name

    Args:
     username:      user's username as string
     real_name:     user's real name as string
     avatar_url:    location of user's avatar
     doc_id:        Document id of an existing Document for this user. By default None, so a new one will be inserted,
                    otherwise, if passed, it will be updated/replaced with new one

    Returns:
     search Document
    """
    # limitation of app engine search, only matches full words, no fuzzy search either
    tokenized_un = ','.join([username[0:i] for i in xrange(1, len(username) + 1)])
    rn = real_name.split()
    rn.append(real_name)
    # tokenizes real name, "john dough", like so (if xrange(3, len(rn) + 1), i don't know if sort order matters for
    #       search performance
    #    ['dou',
    #     'joh',
    #     'doug',
    #     'john',
    #     'dough',
    #     'john ',
    #     'john d',
    #     'john do',
    #     'john dou',
    #     'john doug',
    #     'john dough']
    tokenized_rn = ','.join(sorted(
        set(
            [s[0:i] for s in rn for i in xrange(1, len(s) + 1)]
        ), key=lambda x: (len(x), x)))

    return search.Document(doc_id=doc_id,
        fields=[search.TextField(name='username', value=username),
                search.TextField(name='real_name', value=real_name),
                search.TextField(name='avatar_url', value=avatar_url),
                search.TextField(name='tokenized_un', value=tokenized_un),
                search.TextField(name='tokenized_rn', value=tokenized_rn)])

def add_to_index(document, index_name):
    """adds Document instance to search index with index_name

    Args:
     document:      Document instance
     index_name:    index name as string to add the document to

    Returns:
     True if adding succeeded
     False if adding failed
    """
    try:
        search.Index(name=index_name).put(document)
        logging.info('Adding to index succeeded: %s', document.doc_id)
        return True
    except search.Error as e:
        logging.exception('Adding to index failed: %s' % e.message)

    return False


def find_documents(query_string, limit, index_name="users"):
    """Finds a document containing query string in index

    Args:
     query_string:  query string in Search API format
     limit:         result limit
     index_name:    string name of the index to find the document in, users by default

    Returns:
     SearchResults of the query or None if query failed
    """
    try:
        username_desc = search.SortExpression(
            expression='username',
            direction=search.SortExpression.ASCENDING,
            default_value='aaa')
        real_name_desc = search.SortExpression(
            expression = 'real_name',
            direction=search.SortExpression.ASCENDING,
            default_value='aaa'
        )
        # Sort up to 10 matching results by username then real name in descending order
        sort = search.SortOptions(expressions=[username_desc, real_name_desc], limit=limit)

        options = search.QueryOptions(
            limit=limit,  # the number of results to return
            sort_options=sort,
            returned_fields=['username', 'real_name', 'avatar_url'])

        query = search.Query(query_string=query_string, options=options)

        index = search.Index(name=index_name)

        return index.search(query)
    except search.Error:
        logging.exception('Search failed for: {}'.format(query_string))
    return None

def find_all(index="users"):
    """Find all items in index

    Args:
     index: string index name to search, users by default

    Returns:
     List of Documents in index
    """
    _INDEX_NAME = index

    doc_index = search.Index(name=_INDEX_NAME)

    # Get a list of documents populating, pass ids_only=True to list_documents if want ids only
    documents = [document
                    for document in doc_index.list_documents()]

    if not documents:
        return None
    return documents


def find_users(query):
    """Convenience function, calls find_documents with query

    Args:
     query: query string

    Returns:
     SearchResults
    """
    results = find_documents(query, 10)
    if results:
        return results


def delete_all_in_index(index_name):
    """Delete all the docs in the given index.

    Args:
     index_name:    string name of the index to remove results from
    """
    doc_index = search.Index(name=index_name)

    while True:
        # Get a list of documents populating only the doc_id field and extract the ids.
        document_ids = [document.doc_id
                        for document in doc_index.get_range(ids_only=True)]
        if not document_ids:
            break
            # Remove the documents for the given ids from the Index.
        doc_index.delete(document_ids)

def remove_from_index(doc_id, index_name='users'):
    """Removes document from index,

    Args:
     doc_id:    document id to remove, can find it with find_documents or find_usersc
     index_name:    string name of the index to remove the document from

    Returns:
     False: if there was a DeleteError
     True:  if deleting succeeded
    """
    doc_index = search.Index(name=index_name)
    try:
        doc_index.delete(doc_id)
    except search.DeleteError:
        return False
    return True