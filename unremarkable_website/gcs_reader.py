import re

PAGE_BUCKET = 'unremarkables-pages'

def get_page_exts(pages):
    '''Get the page number and extension for each page.'''
    return {int(re.search('\d+', p).group(0)): p[-3:] for p in pages}

def check_pages(page_exts):
    '''Check that all pages are present and are JPGs.'''
    page_nums = list(page_exts.keys())
    all_pages_present = all([n + 1  in page_nums for n in range(max(page_nums))])
    all_pages_jpg = all([lower(e) in ['jpg','jpeg','png'] for e in page_exts.values()])
    return all_pages_present and all_pages_jpg

def check_artifact_readiness(gcs_client):
    '''Check that everything is in order on GCS to rebuild the website.'''

    artifact_info = {}

    # get pages
    pages = gcs_client.list_blobs(PAGE_BUCKET)
    artifact_info['pages'] = pages

    # get page extensions
    page_exts = get_page_exts(pages)
    artifact_info['page_exts'] = page_exts

    # check that everything is in order
    ready = check_pages(page_exts)

    return ready, artifact_info