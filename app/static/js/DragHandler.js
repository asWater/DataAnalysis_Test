const target = document.getElementById("graphList");
const items = target.getElementsByTagName("li");
let current;

for (let item of items) {
  item.draggable = true;
  item.ondragstart = () => {
    current = item;
    for (let i = 0; i < items.length; i++) {
      if (items[i] !== current) {
        items[i].classList.add("hint");
      }
    }
  };
  item.ondragenter = () => {
    if (item !== current) {
      item.classList.add("active");
    }
  };
  item.ondragleave = () => {
    item.classList.remove("active");
  };
  item.ondragend = () => {
    for (let i = 0; i < items.length; i++) {
      items[i].classList.remove("hint", "active");
    }
  };
  item.ondragover = (ev) => {
    ev.preventDefault();
  };
  item.ondrop = (ev) => {
    ev.preventDefault();
    if (item !== current) {
      let currentPosition = 0;
      let droppedPosition = 0;
      for (let i = 0; i < items.length; i++) {
        if (current === items[i]) {
          currentPosition = i;
        }
        if (item === items[i]) {
          droppedPosition = i;
        }
      }
      if (currentPosition < droppedPosition) {
        item.parentNode.insertBefore(current, item.nextElementSibling);
      } else {
        item.parentNode.insertBefore(current, item);
      }
    }
  };
}