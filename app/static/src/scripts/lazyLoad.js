export default function lazyLoad(){
  console.log("loaded");
  const imgs = document.querySelectorAll('img[data-src]');
  const windowHeight = window.innerHeight;

  for (const img of imgs){
    const i = img.getBoundingClientRect();
    if(i.top > windowHeight){
      img.setAttribute('loading', 'lazy');
    }

    img.setAttribute('src', img.getAttribute('data-src'));
    img.removeAttribute('data-src');
  }

}