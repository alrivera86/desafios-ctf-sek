
var streamSpeed = 10; // Velocidad de la cascada

// Crear la matriz
function createMatrix() {
  var matrix = document.getElementById("matrix");
  var columns = Math.floor(window.innerWidth / (window.innerWidth * 0.05));
  var streams = [];
  for (var i = 0; i < columns; i++) {
    var stream = document.createElement("div");
    stream.className = "stream";
    stream.style.left = i * (window.innerWidth / columns) + "px"; 
    stream.style.top = Math.random() * -1000 + "px";
    streams.push(stream);
    matrix.appendChild(stream);
    for (var j = 0; j < 50; j++) { 
      var letter = document.createElement("div");
      letter.innerHTML = flag[Math.floor(Math.random() * flag.length)];
      stream.appendChild(letter);
    }
  }
}

// Animación de la cascada
function update() {
  for (var i = 0; i < streams.length; i++) {
    var stream = streams[i];
    var letters = stream.children;
    var speed = streamSpeed + Math.random() * streamSpeed;
    var offset = parseInt(stream.style.top) + speed;
    if (offset > window.innerHeight) {
      offset = -200;
    }
    stream.style.top = offset + "px";
    for (var j = 0; j < letters.length; j++) {
      var letter = letters[j];
      letter.style.opacity = 1 - (offset / window.innerHeight);
    }
  }
  requestAnimationFrame(update);
}

function load() {
  createMatrix();
  update();
}

window.onload = load;

// "Despierta, Neo... la Matrix te tiene.
var flag = "flag{b90da5381650dc5cbd779ad0afcea6b2345d1ec973ec5bfc45aa21c624db9f07}"; 
