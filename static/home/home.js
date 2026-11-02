(() => {
 const hero=document.querySelector('#aim-home .ah-hero');
 const tabs=[...hero.querySelectorAll('[role="tab"]')];
 const panels=[...hero.querySelectorAll('[role="tabpanel"]')];
 const backgrounds=['hero-banner_1.webp','hero-banner_2.jpg','hero-banner_3.webp','hero-banner_4.webp'];
 function activate(index,focus=false){tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.tabIndex=i===index?0:-1;panels[i].hidden=i!==index;});hero.style.setProperty('--hero-image',`url('/static/img/Ready-stock/WEBP%20version/${backgrounds[index]}')`);if(focus)tabs[index].focus();}
 tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>activate(i));tab.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight')n=(i+1)%tabs.length;if(e.key==='ArrowLeft')n=(i+tabs.length-1)%tabs.length;if(e.key==='Home')n=0;if(e.key==='End')n=tabs.length-1;if(n!==undefined){e.preventDefault();activate(n,true);}});});
 function moveSlide(delta){const current=tabs.findIndex(tab=>tab.getAttribute('aria-selected')==='true');activate((current+delta+tabs.length)%tabs.length);}
 hero.querySelector('.ah-slide-prev').addEventListener('click',()=>moveSlide(-1));
 hero.querySelector('.ah-slide-next').addEventListener('click',()=>moveSlide(1));
 const pause=hero.querySelector('.ah-slide-pause');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let stopped=reduced.matches,timer=null,visible=true,hovered=false;
 function schedule(){clearInterval(timer);timer=null;if(!stopped&&!document.hidden&&visible&&!hovered)timer=setInterval(()=>moveSlide(1),7000);}
 function syncPause(){pause.setAttribute('aria-pressed',String(stopped));pause.setAttribute('aria-label',stopped?'Пусни автоматичната смяна на слайдовете':'Спри автоматичната смяна на слайдовете');pause.textContent=stopped?'▶':'Ⅱ';schedule();}
 pause.addEventListener('click',()=>{stopped=!stopped;syncPause();});
 hero.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'){hovered=true;schedule();}});
 hero.addEventListener('pointerleave',e=>{if(e.pointerType==='mouse'){hovered=false;schedule();}});
 hero.addEventListener('focusin',e=>{if(e.target!==pause){stopped=true;syncPause();}});
 [...tabs,hero.querySelector('.ah-slide-prev'),hero.querySelector('.ah-slide-next')].forEach(control=>control.addEventListener('click',()=>{stopped=true;syncPause();}));
 document.addEventListener('visibilitychange',schedule);
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;schedule();},{threshold:.2}).observe(hero);
 reduced.addEventListener('change',()=>{if(reduced.matches){stopped=true;syncPause();}});
 let touchStart=null;
 hero.addEventListener('touchstart',e=>{const t=e.changedTouches[0];touchStart={x:t.clientX,y:t.clientY};},{passive:true});
 hero.addEventListener('touchend',e=>{if(!touchStart||e.target.closest('button,a'))return;const t=e.changedTouches[0],dx=t.clientX-touchStart.x,dy=t.clientY-touchStart.y;touchStart=null;if(Math.abs(dx)>55&&Math.abs(dy)<40){moveSlide(dx<0?1:-1);stopped=true;syncPause();}},{passive:true});
 syncPause();
 const track=document.querySelector('.ah-photo-track');
 const prev=document.querySelector('.ah-photo-prev'),next=document.querySelector('.ah-photo-next');
 function galleryState(){prev.disabled=track.scrollLeft<2;next.disabled=track.scrollLeft+track.clientWidth>=track.scrollWidth-3;}
 prev.addEventListener('click',()=>track.scrollBy({left:-track.clientWidth,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'}));
 next.addEventListener('click',()=>track.scrollBy({left:track.clientWidth,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'}));
 track.addEventListener('scroll',galleryState,{passive:true});window.addEventListener('resize',galleryState);galleryState();
})();
