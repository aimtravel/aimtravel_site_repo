(function(){window.__headerPolishLoaded=1;
function set(e,p,v){if(e)e.style.setProperty(p,v,'important')}
function remove(e,p){if(e)e.style.removeProperty(p)}
function label(e){return (e&&e.innerText||'').trim().toUpperCase()}
function update(){
 if(window.innerWidth<801)return;
 var nav=document.getElementById('navbar-normal');if(!nav)return;
 var left=nav.querySelector('.balanced-nav-left'),right=nav.querySelector('.balanced-nav-right'),logo=nav.querySelector('.balanced-logo');
 var leftList=left&&left.querySelector('ul'),rightList=right&&right.querySelector('ul');if(!leftList||!rightList)return;
 var nodes=nav.querySelectorAll('.balanced-nav-left>ul>li,.balanced-nav-right>ul>li'),offers=null,other=null,consult=null;
 for(var i=0;i<nodes.length;i++){var t=label(nodes[i]);if(t.indexOf(' " $ "')===0)offers=nodes[i];if(t.indexOf(' # #!#')===0)other=nodes[i];if(t.indexOf('" !#"&/')===0)consult=nodes[i]}
 var compact=document.body.classList.contains('aim-compact-header');
 if(compact){if(offers&&offers.parentNode!==leftList)leftList.appendChild(offers);set(other,'display','none');set(leftList,'justify-content','space-between');set(rightList,'justify-content','space-between');set(logo,'transform','none')}
 else{if(offers&&offers.parentNode!==rightList)rightList.insertBefore(offers,rightList.firstChild);remove(other,'display');set(leftList,'justify-content','space-between');set(rightList,'justify-content','space-between');remove(logo,'transform')}
 if(consult){var a=consult.querySelector('a');set(consult,'width','184px');set(consult,'min-width','184px');set(consult,'background-color','#b4141b');set(consult,'border-radius','5px');set(consult,'overflow','hidden');set(a,'display','flex');set(a,'align-items','center');set(a,'justify-content','center');set(a,'box-sizing','border-box');set(a,'width','100%');set(a,'height',compact?'36px':'28px');set(a,'padding','0 12px');set(a,'background-color','#b4141b');set(a,'color','#fff');set(a,'white-space','nowrap')}
}
window.addEventListener('scroll',function(){window.requestAnimationFrame(update)},{passive:true});window.addEventListener('resize',update);document.addEventListener('DOMContentLoaded',function(){update();setTimeout(update,200)});setTimeout(update,400);setInterval(update,500);
})();