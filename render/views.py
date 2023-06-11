from django.shortcuts import render
from youtube_transcript_api import YouTubeTranscriptApi
from .forms import YouTubeForm
from django.conf import settings
import openai
import re
openai.api_key = settings.OPEN_AI

from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    video_id = None
    query = urlparse(url)
    if query.hostname == 'www.youtube.com':
        if query.path == '/watch':
            video_id = parse_qs(query.query)['v'][0]
    elif query.hostname == 'youtu.be':
        video_id = query.path[1:]

    return video_id

def gpt3_completion(transcript, engine='gpt-3.5-turbo', temp=0.0, top_p=1.0, tokens=500, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 1
    retry = 0
    prompt = f"using this youtube transcript. Can you make a recipe only if it makes sense to do so. if doesn't make sense please say 'I could not find a recipe in the video'. Please do the html formatting of the content. \n transcript: {transcript}"
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode() # force it to fix any unicode errors

    while True:
        try:
            response = openai.ChatCompletion.create(
                model=engine,
                messages=[
                {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['message']['content'].strip()
            text = re.sub('\s+', ' ', text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def index(request):
    response = ''
    if request.method == "POST":
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['youtube_url']
            print(url)
            id = extract_video_id(url)
            print(id)
            transcript = YouTubeTranscriptApi.get_transcript(id)
            print(transcript)
            response = gpt3_completion(transcript)
    else:
        form = YouTubeForm()

    return render(request, "render/index.html", {'form': form, 'response': response})
