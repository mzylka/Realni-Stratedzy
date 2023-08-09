export default class Tags{
    constructor(){
        this.input_form = document.getElementById("add_post-input_tags");
        this.list_of_tags = document.getElementById("add_post-tags_list").childNodes;
    }

    regEvents(){
        this.list_of_tags.forEach(element => {
            element.addEventListener("click", (event) => this.addTagToInput(event));
        });
    }

    addTagToInput(event){
        const t_text = event.target.innerText;
        console.log(this.input_form.length)
        if (this.input_form.value.length === 0){
            this.input_form.value += t_text;
        }
        else{
            this.input_form.value += "," + t_text;
        }
        event.preventDefault();
    }
}