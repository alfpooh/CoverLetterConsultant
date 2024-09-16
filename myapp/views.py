# myapp/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables
load_dotenv()

def login_view(request):
    if request.method == 'POST':
        testid = os.getenv('TESTID')
        testpw = os.getenv('TESTPW')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == testid and password == testpw:
            return redirect('dashboard')
        else:
            return HttpResponse("Invalid credentials, please try again.")

    return render(request, 'login.html')

def home_view(request):
    return render(request, 'home.html')

def dashboard_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        user_target = request.POST.get('user_target')
        direction = """You are an expert career advisor and professional writer. Your task is to analyze a given CV and job description, assess the candidate's fit, and create a tailored cover letter. Follow these steps:
0. Identify the user's name from the CV and use their first name in the output. The generated cover letter should be written from the user's own perspective, reflecting their personal tone and style.
If CV is not inputted, use the last CV input. 
        
1. If the job description is not well matched with user's experience, you have to warn it. For example, if the job requires a language skill but user cannot speak or write.

2. Analyze the job description:
   - Identify key requirements and skills
   - Note any specific qualifications or experiences requested

3. Review the provided CV:
   - Identify relevant skills, experiences, and qualifications that match the job requirements

4. Assess the candidate's fit:
   - Evaluate how well the candidate's profile matches the job requirements
   - Provide a brief explanation of the fit, highlighting strengths and potential areas for improvement
   - Give an overall assessment of suitability (e.g., excellent fit, good fit, moderate fit, etc.)

5. Generate a tailored cover letter:
   - Use the insights from the job description and CV analysis
   - Highlight the candidate's most relevant experiences and skills
   - Address any specific requirements mentioned in the job description
   - Showcase the candidate's enthusiasm for the position and company
   - Maintain a professional yet engaging tone

6. Output the cover letter in JSON format:
   - Separate each paragraph into individual elements of a JSON array
   - Use the key "coverLetter" for the array of paragraphs

Please provide your analysis and the cover letter based on the following input:
[User will input CV and Job Description here]

Your response should be structured as follows:

1. Job Description Analysis
2. CV Review
3. Fit Assessment
4. JSON-formatted Cover Letter

For the JSON-formatted cover letter, use this structure:
```json
{
  "coverLetter": [
    "Paragraph 1 content",
    "Paragraph 2 content",
    "Paragraph 3 content",
    "Paragraph 4 content"
  ]
}
```

Ensure that each paragraph in the cover letter focuses on a specific aspect of the candidate's qualifications and their relevance to the job description."""

        user_content = "User's cv is > "+user_input+" user wants to apply this position >"+user_target+"Make a nice cover letter. Following this direction" + direction
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return render(request, 'error.html', {'message': 'API key not found'})

        client = OpenAI(api_key=api_key)
        chosen_model = "gpt-4"  # or "gpt-4" if you have access
        try:
            # Use the ChatCompletion API instead of the Assistants API
            response = client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": "You are a career consultant. Address the user as 구직자님. Analyse CV and job description."},
                    {"role": "user", "content": user_content}
                ]
            )

            # Extract the assistant's response
            assistant_response = response.choices[0].message.content

            # Combine both 'response' and 'model' into a single context dictionary
            context = {
                'response': assistant_response,
                'model': chosen_model
            }

            return render(request, 'dashboard.html', context)

        except Exception as e:
            return render(request, 'error.html', {'message': str(e)})

    return render(request, 'dashboard.html')


def process_chat_request(input_text, file=None):
    response = f"ChatGPT Assistant Response to: {input_text}"
    if file:
        response += f" and received file: {file.name}"
    return response

def submit_request_view(request):
    if request.method == "POST":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return render(request, 'error.html', {'message': 'API key not found'})

        client = OpenAI(api_key=api_key)
        user_input = request.POST.get('user_input')

        try:
            # Create a new thread for each request
            thread = client.beta.threads.create()
            thread_id = thread.id

            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id="asst_MqIv1uBTPQHoRCWLJgcVJQuP",
                instructions="Address the user as Dr. Alf."
            )

            # Wait for the run to complete
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            # Retrieve the assistant's messages
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            assistant_message = next((msg for msg in messages if msg.role == "assistant"), None)

            if assistant_message:
                response_content = assistant_message.content[0].text.value
            else:
                response_content = "No response from assistant."

            return render(request, 'dashboard.html', {'response': response_content})

        except Exception as e:
            return render(request, 'error.html', {'message': str(e)})

    return render(request, 'home.html')

# Other view functions...