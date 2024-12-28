from flask import Flask, render_template, request, session
import pandas as pd
import random


app = Flask(__name__)
app.secret_key = 'supersecretkey'


df = pd.read_csv(r"C:\Users\ayush\Downloads\BE_dataset\ML.csv")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        
        if 'questions' not in session or 'correct_answers' not in session or 'question_index' not in session:
            return render_template("index.html", error="Session expired. Please reload the page.")

        
        question_index = session['question_index']
        user_answer = request.form.get("answer")

        
        correct_answer = session['correct_answers'][question_index]
        is_correct = user_answer == correct_answer
        
       
        if 'score' not in session:
            session['score'] = 0
        if is_correct:
            session['score'] += 1

        
        question_index += 1
        session['question_index'] = question_index

       
        if question_index < len(session['questions']):
          
            return render_question(question_index)
        else:
            
            final_score = session['score']
            return render_template("result.html", score=final_score)

    else:
       
        random_rows = df.sample(n=10)

        questions = random_rows['question'].tolist()

        correct_answers = random_rows['answer'].tolist() 

      
        session['questions'] = questions
        session['correct_answers'] = correct_answers
        session['question_index'] = 0  
        session['score'] = 0 
        
        return render_question(session['question_index'])

def render_question(index):
    
    question = session['questions'][index]
    correct_answer = session['correct_answers'][index]

    
    incorrect_answers = df[df['answer'] != correct_answer].sample(n=3)['answer'].tolist()
    
    
    options = incorrect_answers + [correct_answer]
    random.shuffle(options)

    
    session['options'] = options

    return render_template("index.html", question=question, options=options, question_index=index)


if __name__ == "__main__":
    app.run(debug=True)
