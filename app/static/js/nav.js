// nav.js
function toggleBeachesMenu() {
    var menu = document.getElementById('beachesMenu');
    if (menu.classList.contains('hidden')) {
        menu.classList.remove('hidden');
        menu.style.display = 'flex';
    } else {
        menu.classList.add('hidden');
        menu.style.display = 'none';
    }
}

function toggleUserMenu() {
    var menu = document.getElementById('userMenu');
    if (menu.classList.contains('hidden')) {
        menu.classList.remove('hidden');
        menu.style.display = 'flex';
    } else {
        menu.classList.add('hidden');
        menu.style.display = 'none';
    }
}
