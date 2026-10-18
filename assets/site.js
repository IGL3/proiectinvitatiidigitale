/* Scalează invitația (390×844) ca să încapă exact în ecranul fiecărui telefon. */
function fitPhones(root){
  (root||document).querySelectorAll('.screen').forEach(function(screen){
    var frame=screen.querySelector('iframe'); if(!frame) return;
    var apply=function(){ var w=screen.clientWidth; if(w) frame.style.setProperty('--s', w/390); };
    apply();
    if(window.ResizeObserver){ new ResizeObserver(apply).observe(screen); } else { window.addEventListener('resize',apply); }
  });
}

/* Construiește cardurile din lista window.MODELE. base = calea până la folderul templates/. */
function renderModels(container, base){
  var list=window.MODELE||[];
  container.textContent='';
  list.forEach(function(m){
    var url=base+m.slug+'/';
    var card=document.createElement('article'); card.className='card';
    card.innerHTML=
      '<div class="card-phone"><div class="phone" style="--pw:200px"><div class="screen">'+
        '<iframe loading="lazy" tabindex="-1" aria-hidden="true"></iframe></div></div></div>'+
      '<div class="card-body">'+
        '<p class="eyebrow"></p><h3></h3><p class="card-desc"></p>'+
        '<div class="swatches"></div>'+
        '<div class="card-actions"><a class="btn small">Deschide modelul</a></div>'+
      '</div>';
    card.querySelector('iframe').src=url+'?demo=1';
    card.querySelector('iframe').title='Previzualizare '+m.nume;
    card.querySelector('.eyebrow').textContent=m.eveniment;
    card.querySelector('h3').textContent=m.nume;
    card.querySelector('.card-desc').textContent=m.descriere;
    var sw=card.querySelector('.swatches');
    (m.culori||[]).forEach(function(c){ var s=document.createElement('span'); s.style.background=c; sw.appendChild(s); });
    var a=card.querySelector('.card-actions a'); a.href=url; a.target='_blank'; a.rel='noopener';
    container.appendChild(card);
  });
  fitPhones(container);
}

/* Bordura antetului apare după ce începi să derulezi. */
(function(){
  var top=document.querySelector('.top'); if(!top) return;
  var on=function(){ top.classList.toggle('scrolled', window.scrollY>8); };
  on(); window.addEventListener('scroll',on,{passive:true});
})();
