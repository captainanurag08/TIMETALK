/* ===============================
GLOBAL VARIABLES
=================================*/

let chosenSlot = null
let timer = null
let time = 1500

/* ===============================
FIND FREE SLOT (MULTIPLE RESULTS)
=================================*/

function findSlot(){

let day = document.getElementById("day").value
let duration = document.getElementById("duration").value
let startRange = document.getElementById("startRange").value
let endRange = document.getElementById("endRange").value
let title = document.getElementById("title").value
let priority = document.getElementById("priority") ?
document.getElementById("priority").value : "Medium"

fetch("/find_slot",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
day:day,
duration:duration,
start:startRange,
end:endRange
})
})
.then(res => res.json())
.then(data => {

let resultBox = document.getElementById("resultBox")

resultBox.innerHTML = ""

if(data.error){

resultBox.innerHTML = "<p>"+data.error+"</p>"
return

}

/* MULTIPLE SLOT DISPLAY */

data.forEach(slot => {

let card = document.createElement("div")

card.style.padding = "12px"
card.style.margin = "10px 0"
card.style.background = "#1e293b"
card.style.borderRadius = "10px"

card.innerHTML =
"<b>"+slot.start+" - "+slot.end+"</b>"

let btn = document.createElement("button")

btn.innerText = "Add Task"
btn.style.marginLeft = "10px"

btn.onclick = function(){

addTask(
title,
day,
slot.start,
slot.end,
priority
)

}

card.appendChild(btn)

resultBox.appendChild(card)

})

})

}

/* ===============================
ADD TASK FROM SLOT
=================================*/

function addTask(title,day,start,end,priority){

fetch("/add_auto",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
title:title,
day:day,
start:start,
end:end,
priority:priority
})
})
.then(res => res.json())
.then(() => {

alert("Task added successfully!")

window.location = "/schedule"

})

}

/* ===============================
WEEKLY AUTO SCHEDULER
=================================*/

function weeklyAuto(){

let title = document.getElementById("wtitle").value
let duration = document.getElementById("wduration").value
let priority = document.getElementById("wpriority") ?
document.getElementById("wpriority").value : "Medium"

if(!title || !duration){

alert("Enter task name and duration")
return

}

fetch("/weekly_auto",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
title:title,
duration:duration,
priority:priority
})
})
.then(res => res.json())
.then(() => {

alert("Weekly tasks created!")

})

}
function manualWeekly(){

let title = document.getElementById("mtitle").value
let day = document.getElementById("mday").value
let start = document.getElementById("mstart").value
let end = document.getElementById("mend").value
let priority = document.getElementById("mpriority").value

fetch("/manual-weekly",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
title:title,
day:day,
start:start,
end:end,
priority:priority
})
})
.then(r=>r.json())
.then(d=>{
alert("Weekly task created!")
location.reload()
})

}
/* ===============================
FOCUS TIMER (POMODORO)
=================================*/

function startTimer(){

if(Notification.permission !== "granted"){
Notification.requestPermission()
}

if(timer) return

timer = setInterval(() => {

time--

let minutes = Math.floor(time/60)
let seconds = time % 60

document.getElementById("timer").innerText =
String(minutes).padStart(2,"0") + ":" +
String(seconds).padStart(2,"0")

if(time <= 0){

clearInterval(timer)
timer = null

new Notification("Focus session finished!")

}

},1000)

}

function resetTimer(){

clearInterval(timer)

timer = null
time = 1500

let timerBox = document.getElementById("timer")

if(timerBox){
timerBox.innerText = "25:00"
}

}

/* ===============================
TASK REMINDER NOTIFICATIONS
=================================*/

function checkTasks(){

fetch("/tasks_today")
.then(res => res.json())
.then(tasks => {

let now = new Date()

tasks.forEach(task => {

let parts = task.start.split(":")
let taskTime = new Date()

taskTime.setHours(parts[0])
taskTime.setMinutes(parts[1])
taskTime.setSeconds(0)

let diff = (taskTime - now) / 60000

if(diff > 0 && diff < 1){

if(Notification.permission === "granted"){

new Notification(
"Upcoming Task: " + task.title,
{
body: "Starting at " + task.start
}
)

}

}

})

})

}

/* ===============================
START TASK CHECK LOOP
=================================*/

setInterval(checkTasks,60000)

/* ===============================
ASK NOTIFICATION PERMISSION
=================================*/

document.addEventListener("DOMContentLoaded",function(){

if(Notification.permission !== "granted"){
Notification.requestPermission()
}

})
