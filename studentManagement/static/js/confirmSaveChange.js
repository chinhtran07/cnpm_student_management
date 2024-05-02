function confirmSaveChange() {
    if(confirm("Bạn có chắc chắn lưu thay đổi không ?")) {
        document.getElementById('confirmationMessage').style.display = 'block';
        document.getElementById('confirmationMessage').innerHTML = "Đã lưu thay đổi!";
        return true;
    } else {
        return false;
    }
}