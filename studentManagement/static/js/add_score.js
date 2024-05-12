function addToScores(score,type,student_id,subject_id, class_id, period_id){
    fetch ("/TEACHER/api/scores",{
        method:"post",
        body:JSON.stringify({
            "score": score,
            "type": type,
            "student_id": student_id,
            "class_id": class_id,
            "subject_id": subject_id,
            "period_id": period_id
        }),
        headers:{
            "Content-Type":"application/json"
        }
    }).then(res => res.json()).then(data=>{
        if (data.id === 1){
            console.info(data)
            alert(data.message)
        } else if (data.id === 2){
            console.info(data)
            alert(data.message)
        } else if (data.id === 3){
            console.info(data)
            alert(data.message)
        }else if (data.id === 4){
            console.info(data)
            alert(data.message)
        }
    })
}

function createScore (subject_id, period_id){
    fetch(`/TEACHER/api/save_scores?subject_id=${subject_id}&period_id=${period_id}`,{

        method:"post"
    }).then(res => res.json()).then(data=>{
        if (data.status === 200){
            alert("Xác nhận thành công !!!! ")
            location.reload()
        } else{
        alert("Xác nhận không thành công !!!! ")
        console.info(data)
        }

    })
}