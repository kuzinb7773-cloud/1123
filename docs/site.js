// ensure profile link present in header nav on every page
document.addEventListener('DOMContentLoaded', function(){
  try{
    var nav = document.querySelector('.site-header .nav');
    if(!nav) nav = document.querySelector('.nav');
    if(!nav) return;
    var exists = Array.from(nav.querySelectorAll('a')).some(a=>a.getAttribute('href') === 'profile.html');
    if(!exists){
      var a = document.createElement('a');
      a.href = 'profile.html';
      a.className = 'nav-profile';
      a.textContent = 'Личный кабинет';
      nav.appendChild(a);
    }
  }catch(e){console && console.error(e)}

  // show/hide instructions link based on auth
  window.updateInstructionsNav();
});

// Dynamic "Инструктаж и тесты" link — visible only when logged in
window.updateInstructionsNav = function(){
  try{
    var nav = document.querySelector('.site-header .nav');
    if(!nav) nav = document.querySelector('.nav');
    if(!nav) return;
    var existing = nav.querySelector('a[href="instructions.html"]');
    var loggedIn = !!localStorage.getItem('currentUser');
    if(loggedIn && !existing){
      var a = document.createElement('a');
      a.href = 'instructions.html';
      a.textContent = 'Инструктаж и тесты';
      // insert before "Личный кабинет" link
      var profileLink = nav.querySelector('a[href="profile.html"]');
      if(profileLink){
        nav.insertBefore(a, profileLink);
      } else {
        nav.appendChild(a);
      }
    } else if(!loggedIn && existing){
      existing.remove();
    }
  }catch(e){console && console.error(e)}
};

// --- Dark theme toggle ---
(function(){
  var STORAGE_KEY = 'theme';

  function applyTheme(theme){
    document.documentElement.setAttribute('data-theme', theme);
    var btn = document.getElementById('theme-toggle');
    if(btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  // Apply saved theme BEFORE DOMContentLoaded to avoid flash
  var saved = localStorage.getItem(STORAGE_KEY) || 'light';
  document.documentElement.setAttribute('data-theme', saved);

  document.addEventListener('DOMContentLoaded', function(){
    // Create toggle button and insert into header
    var header = document.querySelector('.header-inner');
    if(!header) return;

    var btn = document.createElement('button');
    btn.id = 'theme-toggle';
    btn.className = 'theme-toggle-btn';
    btn.title = 'Переключить тему';
    btn.textContent = saved === 'dark' ? '☀️' : '🌙';
    btn.addEventListener('click', function(){
      var current = document.documentElement.getAttribute('data-theme') || 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
    });

    header.appendChild(btn);
  });
})();
