import re

WEBSITE_BUCKET = 'www.unremarkables.com'

SELECTOR_STUB = '''<option value="page{current_page}.html" selected>Go to Page...</option>'''
SELECTOR_LINE =  '''\n\t<option value="page{page_num}.html">Page {page_num}</option>'''

def upload_blob_from_memory(gcs_client, bucket_name, contents, destination_blob_name):
    '''Uploads a file to the bucket.'''

    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)


def generate_selector(page_num, page_exts, selector_stub, selector_line):
    '''Generate the selector line of HTML.'''
    selector = selector_stub.format(current_page=page_num)
    for page in page_exts.keys():
        selector += selector_line.format(page_num=page)
    return selector


def generate_page(page_num, page_exts, template, selector_stub, selector_line):
    '''Generate a comic page's HTML.'''

    # generate selector text
    selector = generate_selector(page_num, page_exts, selector_stub, selector_line)

    # build relative links
    if page_num == 1:
        link_first = ''
        link_prev = ''
    else:
        link_first = 'page1.html'
        link_prev = 'page{}.html'.format(page_num - 1)
    if page_num == max(page_exts.keys()):
        link_next = ''
        link_latest = ''
    else:
        link_next = 'page{}.html'.format(page_num + 1)
        link_latest = 'page{}.html'.format(max(page_exts.keys()))
        
    args = {
        'link_first': link_first,
        'link_previous': link_prev,
        'selector_guts': selector,
        'link_next': link_next,
        'link_latest': link_latest,
        'page_num': page_num,
        'image_ext': page_exts[page_num]
    }
    return template.format(**args)

    
def generate_index(page_exts, index_template, selector_stub, selector_line):
    '''Generate the index page's HTML.'''
    # generate selector text
    selector = generate_selector(1, page_exts, selector_stub, selector_line)
    link_latest = 'page{}.html'.format(max(page_exts.keys()))
    args = {
        'selector_guts': selector,
        'link_latest': link_latest,
    }
    return index_template.format(**args)


def write_index(gcs_client, page_exts, index_template, selector_stub, selector_line):
    '''Write the index html file to GCS.'''
    page_guts = generate_index(page_exts, index_template, selector_stub, selector_line)
    key = 'index.html'
    upload_blob_from_memory(gcs_client, WEBSITE_BUCKET, page_guts, key)


def write_page(gcs_client, page_num, page_exts, page_template, selector_stub, selector_line):
    '''Write a single comic page html file to GCS.'''
    page_guts = generate_page(page_num, page_exts, template, selector_stub, selector_line)
    key = 'page{}.html'.format(page_num)
    upload_blob_from_memory(gcs_client, WEBSITE_BUCKET, page_guts, key)


def build_website(artifact_info, gcs_client):
    '''Rebuild the entire static website in GCS using the provided templates.'''
    
    pages = artifact_info.get('pages')
    page_exts = artifact_info.get('pages_exts')

    with open('templates/page_template.txt','r') as f:
        page_template = f.read()

    with open('index_template.txt','r') as f:
        index_template = f.read()

    # write pages
    for page_num in page_exts.keys():
        write_page(gcs_client, page_num, page_exts, page_template,
                   SELECTOR_STUB, SELECTOR_LINE)

    # write index
    write_index(gcs_client, page_exts, index_template,
                SELECTOR_STUB, SELECTOR_LINE)

    print('Generated sites for all {} pages!'.format(max(page_exts.keys())))
