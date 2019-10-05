from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
from google.cloud import storage

""" Based on code published by Sundar Krishnan
    https://towardsdatascience.com/how-to-use-google-speech-to-text-api-to-transcribe-long-audio-files-1c886f4eb3e9
"""

def transcribe_gcs(bucketname, audio_file_name):
    """ Asynchronously transcribes audio from cloud storage uri 
        writes transcribed audio to text file
    """
    # Instantiates a client
    client = speech.SpeechClient()

    gcs_uri = 'gs://' + bucketname + '/' + audio_file_name

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=32000,
        language_code='en-US',
        diarization_speaker_count=2,
        enable_speaker_diarization=True,
        enable_automatic_punctuation=True,
        model='video'
    )

    operation = client.long_running_recognize(config, audio)
    print('Waiting for operation to complete...')
    response = operation.result(timeout=10000)

    with open('../data/transcripts/results_{}.txt'.format(audio_file_name), 'a+') as out_file:
        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        result = response.results[-1]
        # First alternative has words tagged with speakers
        alternative = result.alternatives[0]
        transcript = ''
        tag=1
        count=0
        # Print the speaker_tag again when speaker changes
        for word in alternative.words:
            if word.speaker_tag != tag: # it has changed
                transcript += "\nSpeaker {}: ".format(word.speaker_tag) + word.word + " "
                tag = word.speaker_tag
            else:
                transcript += word.word + " "
        out_file.write(transcript)

def create_bucket(bucket_name):
    # Instantiates a client
    storage_client = storage.Client()
    # Creates the new bucket
    bucket = storage_client.create_bucket(bucket_name)
    print('Bucket {} created.'.format(bucket.name))

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    CHUNK_SIZE = 10485760 # upload in 10MB chunks
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name, chunk_size=CHUNK_SIZE)
    blob.upload_from_filename(source_file_name)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()


# ID for current participant
p_id = "PE"

# main routine
upload_blob('impars-audio', '../data/raw/{}/audio_only.flac'.format(p_id), p_id)
transcribe_gcs('impars-audio', p_id)
delete_blob('impars-audio', p_id)
