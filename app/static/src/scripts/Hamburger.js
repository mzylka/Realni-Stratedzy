export default class Hamburger{
    constructor(){
        this.hamburger = document.querySelector(".header__hamburger");
        this.menu = document.querySelector(".header__menu");
    }

    regEvents(){
        this.hamburger.addEventListener("click", () => this.toggleTheMenu());
        //window.addEventListener("resize", () => this.onResize());
    }

    toggleTheMenu(){
        this.menu.classList.toggle("hidden");
    }

    onResize(){
        let width = window.innerWidth;

        if(width >= 900){
            this.menu.classList.remove("header__menu--is-visible");
        }
    }
}