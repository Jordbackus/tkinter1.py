import customtkinter
import json
import hashlib
from random_id import random_id
import matplotlib.pyplot as plt
from customtkinter import CTkImage
from PIL import Image
customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")
import sqlite3
con = sqlite3.connect("quiz.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS userData(id,name, password)")
cur.execute("CREATE TABLE IF NOT EXISTS quizData(userId,quizName,score)")
app=customtkinter.CTk()
app.title("Quiz Application")
app.geometry("600x400")
app.columnconfigure(0,weight=1)

subjects=["History","Science","General Knowledge","Cricket","Movies","Entertainment"]
currentWidgets=[]
correctAns=[]
choosenAns=[]
data={}
currentUser=()
activeQuiz=""

import random
def getRandomQ(arr, num_questions=5):
    return random.sample(arr, num_questions)

index=0
selectedQuestion=[]

def destroyWidgets():
    if(len(currentWidgets)):
        for c in currentWidgets:
            c.destroy()

def hash_password(password):
    # Hash the password using SHA-256 algorithm
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def exitFn():
        destroyWidgets()
        renderChoices()
        selectedQuestion.clear()
        global index
        index=0
        choosenAns.clear()
        correctAns.clear()

def exitApp():
    destroyWidgets()
    renderLogin()

def choosenAnsFn(ans):
    choosenAns.append(ans)
    renderQuestion()

def renderQuestion():
    global index
    if(index>len(selectedQuestion)-1):
        checkAns()
        return
    destroyWidgets()
    tempFrame=customtkinter.CTkFrame(master=app)
    tempFrame.grid(row=1,column=0)
    currentWidgets.append(tempFrame)
    q=customtkinter.CTkLabel(text=f"Question {index+1}: {selectedQuestion[index]["q"]}",master=tempFrame,font=customtkinter.CTkFont(size=15))
    q.grid(row=0,column=0,padx=50,pady=20)
    for i,ans in enumerate(selectedQuestion[index]["a"]):
        selectBtn=customtkinter.CTkButton(text=f"{ans}",master=tempFrame,width=100,command=lambda ans=ans:choosenAnsFn(ans))
        selectBtn.grid(row=i+1,column=0,pady=5)
    index+=1
    paginationFrame=customtkinter.CTkFrame(master=tempFrame)
    paginationFrame.grid(row=6,column=0,pady=10)

    exitBtn=customtkinter.CTkButton(master=paginationFrame,text="Exit",command=exitFn)
    exitBtn.grid(row=0,column=0,padx=30,pady=10)

    submitBtn=customtkinter.CTkButton(text="Submit",master=paginationFrame,command=checkAns)
    submitBtn.grid(row=0,column=1,padx=30,pady=10)

def renderQuestions(subject):
    global activeQuiz
    activeQuiz=subject
    allQ=data[subject]
    selectedQuestion.extend(getRandomQ(allQ))
    for q in selectedQuestion:
        correctAns.append(q["c"])
    renderQuestion()

def renderDashboard():
    destroyWidgets()
    
    cur.execute("SELECT * from quizData where userId=?", (currentUser[0],))
    data = cur.fetchall()
    headers = ["S.No.", "Topic", "Score", "Maximum"]  
    tempFrame = customtkinter.CTkFrame(master=app)
    tempFrame.grid(row=0, column=0, pady=50)
    currentWidgets.append(tempFrame)
    dashboardHeader = customtkinter.CTkLabel(text="DASHBOARD", master=tempFrame)
    dashboardHeader.grid(row=0, column=0, padx=20, pady=20, columnspan=5)
    dashboardHeader.configure(font=("Arial", 20, "bold"))
    
    for i, item in enumerate(headers):
        label = customtkinter.CTkButton(master=tempFrame, text=item, width=64)
        label.grid(row=1, column=i, padx=30, pady=10)
    
    for i, record in enumerate(data):
        s = customtkinter.CTkLabel(master=tempFrame, text=i + 1)
        s.grid(row=i + 2, column=0, padx=20, pady=10)
        
        topic = customtkinter.CTkLabel(master=tempFrame, text=record[1].upper())
        topic.grid(row=i + 2, column=1, padx=20, pady=10)
        
        score = customtkinter.CTkLabel(master=tempFrame, text=record[2])
        score.grid(row=i + 2, column=2, padx=20, pady=10)
        
        maxVal = customtkinter.CTkLabel(master=tempFrame, text="5")
        maxVal.grid(row=i + 2, column=3, padx=20, pady=10)

    graph_button = customtkinter.CTkButton(master=tempFrame, text="See Marks (Graph)", command=showMarksGraph)
    graph_button.grid(row=i + 3, column=0, columnspan=5, pady=20)
    exitBtn = customtkinter.CTkButton(master=tempFrame, text="Exit", command=renderChoices)
    exitBtn.grid(row=i + 4, column=0, padx=20, pady=30, columnspan=5)

graph_widgets = []  

def showMarksGraph():
    global graph_widgets
    destroyWidgets()  

    cur.execute("SELECT * from quizData where userId=?", (currentUser[0],))
    data = cur.fetchall()

    quiz_names = [record[1] for record in data]
    scores = [record[2] for record in data]

    plt.bar(quiz_names, scores, color='blue')
    plt.xlabel('Quiz Name')
    plt.ylabel('Score')
    plt.title('Quiz Scores')
    plt.show()

    renderDashboard()

def exitGraph():
    global graph_widgets
    for widget in graph_widgets:
        widget.destroy()
    renderDashboard()

def renderChoices():
    global data 
    for widget in currentWidgets:
        widget.destroy()
    
    title = customtkinter.CTkLabel(text=f"Welcome to the quiz, {currentUser[1]}", master=app, font=customtkinter.CTkFont(size=30))
    title.grid(pady=30, padx=30, row=0, column=0)
    currentWidgets.append(title)
    
    tempFrame = customtkinter.CTkFrame(master=app, corner_radius=10)
    tempFrame.grid(padx=30, pady=20, row=1, column=0)
    currentWidgets.append(tempFrame)

    genre_count = len(subjects)
    total_questions = len(data)
    
    for i, subject in enumerate(subjects):
        choiceFrame = customtkinter.CTkFrame(master=tempFrame, corner_radius=20)
        nameFont = customtkinter.CTkFont(size=30)
        name = customtkinter.CTkLabel(text=subject.upper(), master=choiceFrame, font=nameFont)
        name.grid(row=0, column=0, padx=10, pady=5)
        
        startBtn = customtkinter.CTkButton(master=choiceFrame, text="Start quiz", command=lambda subject=subject: renderQuestions(subject))
        startBtn.grid(row=1, column=0, padx=10, pady=20)
        choiceFrame.grid(row=i % 2, column=i % 3, padx=20, pady=20)
    
    exitBtn = customtkinter.CTkButton(text="Exit", command=exitApp, master=tempFrame)
    exitBtn.grid(row=2, column=0, pady=20, padx=50)
    
    dashboard = customtkinter.CTkButton(text="DASHBOARD", master=tempFrame, command=renderDashboard)
    dashboard.grid(row=2, column=1, pady=20, padx=50, columnspan=1)
    dashboard.configure(font=("Arial", 14, "bold"))

    f = open("data.json")
    fileData = json.load(f)
    data = fileData  
    f.close()

    info_label = customtkinter.CTkLabel(text=f"This quiz contains {genre_count} genres and has a total of 5 questions. You can opt whichever topic you want.", master=tempFrame, font=customtkinter.CTkFont(size=16))
    info_label.grid(row=3, column=0, columnspan=3, padx=20, pady=20)

tempFrame=None
name=None
password=None

def renderLogin():
    global tempFrame,name,password
    title=customtkinter.CTkLabel(text=f"Quiz Application In TKinter",master=app,font=customtkinter.CTkFont(size=30))
    title.grid(pady=30,padx=30,row=0,column=0)
    currentWidgets.append(title)
    tempFrame = customtkinter.CTkFrame(master=app, corner_radius=10)
    tempFrame.grid(padx=30, pady=20, row=1, column=0)
    currentWidgets.append(tempFrame)

    name = customtkinter.CTkEntry(master=tempFrame, placeholder_text="Enter your username")
    name.grid(row=0, column=0, padx=30, pady=10)

    password = customtkinter.CTkEntry(master=tempFrame, placeholder_text="Enter a four-digit PIN", show="*")
    password.grid(row=1, column=0, padx=30, pady=10)

    def handler():
        username = name.get()
        pin = password.get()
        cur.execute("SELECT * FROM userData WHERE name=?", (username,))
        isUsernameExist=cur.fetchone()
        if isUsernameExist:
            if len(pin) != 4 or not pin.isdigit():
                print("PIN should be a four-digit number.")
                return
            cur.execute("SELECT * FROM userData WHERE name=? AND password=?", (username, pin))
            existing_user = cur.fetchone()
            if existing_user:
                print(existing_user)
                global currentUser
                currentUser=existing_user
                destroyWidgets()
                renderChoices()
                return
            else:
                print("Username already exists OR Wrong password")
                return
        else:
             if len(pin) != 4 or not pin.isdigit():
                print("PIN should be a four-digit number.")
                return
             userId=random_id(5)
             cur.execute("INSERT INTO userData(id,name, password) VALUES (?, ?,?)", (userId,username,pin))
             con.commit()
             currentUser=(userId,username,pin)
             destroyWidgets()
             renderChoices()
             return
           
    nextBtn = customtkinter.CTkButton(master=tempFrame, text="Login", command=handler)
    nextBtn.grid(row=2, column=0, padx=30, pady=10)

def calculateScore():
    score=0
    for ans in correctAns:
        if ans in choosenAns:
            score+=1
    return score

def checkAns():
    destroyWidgets()
    tempFrame = customtkinter.CTkFrame(master=app, width=400, height=300)
    tempFrame.grid(row=1, column=0)
    currentWidgets.append(tempFrame)
    score=calculateScore()
    cur.execute("INSERT INTO quizData(userId,quizName,score) VALUES (?,?,?)", (currentUser[0],activeQuiz,score ))
    con.commit()
    resulth = customtkinter.CTkLabel(master=tempFrame, text="Quiz Result", font=customtkinter.CTkFont(size=20))
    resulth.grid(row=0, column=0, padx=20, pady=20)
    exitBtn=customtkinter.CTkButton(master= tempFrame,text="Exit the Quiz",command=exitFn)
    exitBtn.grid(row=3,column=0,padx=10,pady=20)

    result=customtkinter.CTkLabel(master=tempFrame,text=f"You got {score} out of 5 questions correct !!")
    result.grid(row=1,column=0,padx=20,pady=20)

    review_btn = customtkinter.CTkButton(master=tempFrame, text="Review Answers", command=reviewAnswers)
    review_btn.grid(row=2, column=0, columnspan=3, pady=20)

def reviewAnswers():
    destroyWidgets()
    tempFrame = customtkinter.CTkFrame(master=app, width=400, height=300)
    tempFrame.grid(row=1, column=0)
    currentWidgets.append(tempFrame)

    for i, (question, correct_answer, chosen_answer) in enumerate(zip(selectedQuestion, correctAns, choosenAns), start=1):
        question_text = f"{i}. {question['q']}"
        question_label = customtkinter.CTkLabel(master=tempFrame, text=question_text, font=customtkinter.CTkFont(size=12))
        question_label.grid(row=i, column=0, padx=20, pady=5)

        correct_answer_text = f"Correct Answer: {correct_answer}"
        correct_answer_label = customtkinter.CTkLabel(master=tempFrame, text=correct_answer_text, font=customtkinter.CTkFont(size=12), fg_color="green")
        correct_answer_label.grid(row=i, column=1, padx=20, pady=5)

        chosen_answer_text = f"Your Answer: {chosen_answer}"
        chosen_answer_label = customtkinter.CTkLabel(master=tempFrame, text=chosen_answer_text, font=customtkinter.CTkFont(size=12), fg_color="red" if chosen_answer != correct_answer else "green")
        chosen_answer_label.grid(row=i, column=2, padx=20, pady=5)

    score_label = customtkinter.CTkLabel(master=tempFrame, text=f"Your Score: {sum(1 for ans in correctAns if ans in choosenAns)} / {len(correctAns)}", font=customtkinter.CTkFont(size=16))
    score_label.grid(row=i + 1, column=0, columnspan=3, pady=10)

    exit_btn = customtkinter.CTkButton(master=tempFrame, text="Exit the Quiz", command=exitFn)
    exit_btn.grid(row=i + 2, column=0, columnspan=3, pady=20)
renderLogin()   

app.mainloop()