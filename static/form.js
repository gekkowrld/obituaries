let obituary = document.forms.obituary;
let ob_name = true, ob_content = true, ob_author = true, ob_slug = true;
let submit_btn = document.querySelector("#submit_btn");
let dob = "", dod = "";

obituary.name.addEventListener("input", () => {
  let val = obituary.name.value;
  if (val.length < 7) {
    obituary.name.classList.add("error")
    ob_name=false;
  }else {
    obituary.name.classList.remove("error")
    ob_name=true;
  }
})

obituary.content.addEventListener("input", () => {
  let val = obituary.content.value;
  if (val.length < 15) {
    obituary.content.classList.add("error");
    ob_content = false;
  }else{
    obituary.content.classList.remove("error");
    ob_content=true;
  }
})

obituary.author.addEventListener("input", () => {
  let val = obituary.author.value;
  if (val.length < 5) {
    obituary.author.classList.add("error");
    ob_author = false;
  }else{
    obituary.author.classList.remove("error");
    ob_author=true;
  }
})

obituary.slug.addEventListener("input", () => {
  let val = obituary.slug.value;
  if (val.length < 10) {
    obituary.slug.classList.add("error");
    ob_slug = false;
  }else{
    obituary.slug.classList.remove("error");
    ob_slug=true;
  }
})

obituary.dob.addEventListener("input", () => {
  dob = obituary.dob.value;
})
obituary.dod.addEventListener("input", () => {
  dod = obituary.dod.value;
})

obituary.addEventListener("input", () => {
      let dobDate = new Date(dob);
    let dodDate = new Date(dod);
if (!!!dod.trim() || !!!dob.trim() || dobDate >= dodDate || !ob_name || !ob_content || !ob_author || !ob_slug) {
    submit_btn.classList.add("disable")
    submit_btn.disabled = true;
  }else {
    submit_btn.classList.remove("disable")
    submit_btn.disabled = false;
  }
})
