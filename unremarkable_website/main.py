from google.cloud import storage

from builder import build_website
from email_funcs import send_confirmation_email, send_error_email
from gcs_reader import check_artifact_readiness

def main(request):
    '''Process the GCS notification when a new page jpg is uploaded
        and rebuild the website.'''

    gcs_client = storage.Client()

    ready, artifact_info = check_artifact_readiness(gcs_client)

    if ready:
        build_website(artifact_info, gcs_client)
        send_confirmation_email(request)
        return 'Website rebuilt!', 200

    else:
        print('Some pages are missing or formatted incorrectly!')
        send_error_email(artifact_info)
        return 'Unable to rebuild website!', 500

