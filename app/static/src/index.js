import Hamburger from "./scripts/Hamburger";
import lazyLoad from "./scripts/lazyLoad";

window.addEventListener("DOMContentLoaded", lazyLoad)

const hamburger = new Hamburger();
hamburger.regEvents();