/* Scalează invitația (390×844) ca să încapă exact în ecranul fiecărui telefon. */
function fitPhones(root){
  (root||document).querySelectorAll('.screen').forEach(function(screen){
    var frame=screen.querySelector('iframe'); if(!frame) return;
    var apply=function(){ var w=screen.clientWidth, h=screen.clientHeight; if(!w) return; var k=w/390; frame.style.setProperty('--s', k); frame.style.height=Math.ceil(h/k)+'px'; };
    apply();
    if(window.ResizeObserver){ new ResizeObserver(apply).observe(screen); } else { window.addEventListener('resize',apply); }
  });
}

/* Construiește cardurile din lista window.MODELE. base = calea până la folderul templates/. */
function renderModels(container, base, contactHref){
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
        '<div class="card-actions"><button type="button" class="btn small">Vezi demo pe telefon</button></div>'+
      '</div>';
    card.querySelector('iframe').src=url+'?demo=1&v='+(m.v||'1');
    card.querySelector('iframe').title='Previzualizare '+m.nume;
    card.querySelector('.eyebrow').textContent=m.eveniment;
    card.querySelector('h3').textContent=m.nume;
    card.querySelector('.card-desc').textContent=m.descriere;
    card.querySelector('.card-actions button').addEventListener('click',function(){ openDemo(m, url, contactHref||'#contact'); });
    container.appendChild(card);
  });
  fitPhones(container);
}

/* Demo mare: modelul rulează într-un telefon deasupra paginii, fără să deschidă invitația propriu-zisă. */
var demoBox=null, lastFocus=null;
function openDemo(m, url, contactHref){
  if(!demoBox){
    demoBox=document.createElement('div'); demoBox.className='demo-modal'; demoBox.hidden=true;
    demoBox.setAttribute('role','dialog'); demoBox.setAttribute('aria-modal','true');
    demoBox.innerHTML=
      '<div class="demo-inner">'+
        '<div class="phone demo-phone"><div class="screen"><iframe></iframe></div></div>'+
        '<div class="demo-side">'+
          '<p class="eyebrow"></p><h2></h2><p class="demo-desc"></p>'+
          '<p class="demo-hint">Invitația rulează singură. Atingeți ecranul telefonului ca s-o răsfoiți voi.</p>'+
          '<div class="demo-actions"><a class="btn">Vreau acest model</a><button type="button" class="btn ghost demo-close">Închide</button></div>'+
        '</div>'+
      '</div>';
    document.body.appendChild(demoBox);
    demoBox.addEventListener('click',function(e){ if(e.target===demoBox) closeDemo(); });
    demoBox.querySelector('.demo-close').addEventListener('click',closeDemo);
    demoBox.querySelector('.demo-actions a').addEventListener('click',closeDemo);
    document.addEventListener('keydown',function(e){ if(e.key==='Escape' && demoBox && !demoBox.hidden) closeDemo(); });
  }
  lastFocus=document.activeElement;
  demoBox.setAttribute('aria-label','Demo '+m.nume);
  demoBox.querySelector('.eyebrow').textContent=m.eveniment;
  demoBox.querySelector('h2').textContent=m.nume;
  demoBox.querySelector('.demo-desc').textContent=m.descriere;
  demoBox.querySelector('.demo-actions a').href=contactHref;
  var f=demoBox.querySelector('iframe'); f.title='Demo '+m.nume; f.src=url+'?demo=1&sunet=1&v='+(m.v||'1');
  demoBox.hidden=false; document.documentElement.classList.add('modal-open');
  fitPhones(demoBox);
  demoBox.querySelector('.demo-close').focus();
}
function closeDemo(){
  if(!demoBox) return;
  demoBox.hidden=true; document.documentElement.classList.remove('modal-open');
  demoBox.querySelector('iframe').src='about:blank';
  if(lastFocus) lastFocus.focus();
}

/* Bordura antetului apare după ce începi să derulezi. */
(function(){
  var top=document.querySelector('.top'); if(!top) return;
  var on=function(){ top.classList.toggle('scrolled', window.scrollY>8); };
  on(); window.addEventListener('scroll',on,{passive:true});
})();
