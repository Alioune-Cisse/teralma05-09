function ajouter_val(){

var span = document.createElement('SPAN');
    textes = document.getElementById("tags").value
    //span.innerHTML = '<input type="checkbox" id="'+textes+'"class="chk-btn" name="choix" value="'+textes+'" checked/><label for="choix">"'+textes+'"</label><br>'
    span.innerHTML = '<input type="checkbox" id="'+textes+'" class="chk-btn" name="choix" value="'+textes+'" checked/><label for="'+textes+'">'+textes+'</label>'
    span.id = name;
    span.className = "filelist";
    document.getElementById("tags").value = ""
 /*   span.onclick = function(){
    span.text = "Blabla"
    document.getElementById("all_vals").appendChild(span);

}*/
document.getElementById("sc").appendChild(span);
}