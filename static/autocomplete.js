document.getElementById('program').addEventListener('keyup', e => {
    index.value = e.target.selectionStart;
})
document.getElementById('program').addEventListener('mouseleave', e => { 
    let index = document.getElementById('index');
    index.value = e.target.selectionStart;
})
document.getElementById('program').addEventListener('mouseup', e => { 
    let index = document.getElementById('index');
    index.value = e.target.selectionStart;
})