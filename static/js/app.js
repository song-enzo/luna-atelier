// LUNA ATELIER — App JS
(function(){
'use strict';

// ---- Touch Carousel ----
function initCarousels(){
  document.querySelectorAll('.pdp-carousel').forEach(function(wrap){
    var track = wrap.querySelector('.track');
    if(!track) return;
    var slides = track.children;
    if(slides.length < 2) return;

    var idx = 0, startX = 0, currentX = 0, dragging = false;

    function goTo(i){
      idx = ((i % slides.length) + slides.length) % slides.length;
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      var dots = wrap.querySelectorAll('.pdp-dots span');
      dots.forEach(function(d,j){ d.classList.toggle('active',j===idx); });
    }

    function slide(dir){ goTo(idx + dir); }

    // Arrows
    var prev = wrap.querySelector('.pdp-arrow-prev');
    var next = wrap.querySelector('.pdp-arrow-next');
    if(prev) prev.addEventListener('click',function(e){e.stopPropagation();slide(-1);});
    if(next) next.addEventListener('click',function(e){e.stopPropagation();slide(1);});

    // Touch
    track.addEventListener('touchstart',function(e){
      startX = e.touches[0].clientX;
      currentX = startX;
      dragging = true;
      track.style.transition = 'none';
    }, {passive:true});

    track.addEventListener('touchmove',function(e){
      if(!dragging) return;
      currentX = e.touches[0].clientX;
      var diff = currentX - startX;
      var pct = -idx * 100 + (diff / track.offsetWidth * 100);
      track.style.transform = 'translateX(' + pct + '%)';
    }, {passive:true});

    track.addEventListener('touchend',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.2){
        slide(diff < 0 ? 1 : -1);
      } else {
        goTo(idx);
      }
    }, {passive:true});

    // Mouse drag (desktop)
    track.addEventListener('mousedown',function(e){
      startX = e.clientX; currentX = startX; dragging = true;
      track.style.transition = 'none';
    });
    track.addEventListener('mousemove',function(e){
      if(!dragging) return;
      currentX = e.clientX;
      var diff = currentX - startX;
      track.style.transform = 'translateX(' + (-idx * 100 + diff/track.offsetWidth*100) + '%)';
    });
    track.addEventListener('mouseup',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.2){ slide(diff < 0 ? 1 : -1); }
      else { goTo(idx); }
    });
    track.addEventListener('mouseleave',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      goTo(idx);
    });
  });
}

// ---- Qty Stepper ----
function initQty(){
  document.querySelectorAll('.qty-bar').forEach(function(bar){
    var val = bar.querySelector('.val');
    var dec = bar.querySelector('.qty-dec');
    var inc = bar.querySelector('.qty-inc');
    if(!val || !dec || !inc) return;
    dec.addEventListener('click',function(){
      var v = parseInt(val.textContent) || 1;
      if(v > 1) val.textContent = v - 1;
    });
    inc.addEventListener('click',function(){
      var v = parseInt(val.textContent) || 1;
      val.textContent = v + 1;
    });
  });
}

// ---- Size Select ----
function initSize(){
  document.querySelectorAll('.size-grid').forEach(function(grid){
    grid.addEventListener('click',function(e){
      var btn = e.target.closest('.size-btn');
      if(!btn) return;
      grid.querySelectorAll('.size-btn').forEach(function(b){ b.classList.remove('active'); });
      btn.classList.add('active');
      var hidden = grid.parentElement.querySelector('input[name="size"]');
      if(hidden) hidden.value = btn.textContent.trim();
    });
  });
}

// ---- Swatch Select ----
function initSwatches(){
  document.querySelectorAll('.swatch-row').forEach(function(row){
    row.addEventListener('click',function(e){
      var sw = e.target.closest('.swatch-circle');
      if(!sw || sw.classList.contains('active')) return;
      row.querySelectorAll('.swatch-circle').forEach(function(s){ s.classList.remove('active'); });
      sw.classList.add('active');
      var hidden = row.parentElement.querySelector('input[name="color"]');
      if(hidden) hidden.value = sw.getAttribute('data-color') || '';
    });
  });
}

// ---- Order Form: single/multi mode ----
function initOrderForm(){
  var form = document.getElementById('orderForm');
  if(!form) return;

  var modeRadios = form.querySelectorAll('input[name="order_mode"]');
  var singleSection = document.getElementById('singleModeFields');
  var multiSection = document.getElementById('multiModeFields');
  var swatchList = document.getElementById('swatchList');
  var itemsField = document.getElementById('itemsField');
  var totalQty = document.getElementById('totalQty');

  if(modeRadios.length) modeRadios.forEach(function(r){
    r.addEventListener('change',function(){
      if(this.value === 'single'){
        if(singleSection) singleSection.style.display = 'block';
        if(multiSection) multiSection.style.display = 'none';
      } else {
        if(singleSection) singleSection.style.display = 'none';
        if(multiSection) multiSection.style.display = 'block';
      }
    });
  });
}

// ---- Confirm Receipt ----
function initConfirm(){
  document.querySelectorAll('.confirm-form').forEach(function(f){
    f.addEventListener('submit',function(e){
      if(!confirm('确认收货后订单将标记为已完成，确定吗？')) e.preventDefault();
    });
  });
}

// ---- Cropper: Upload & Color Management ----
var colorItems = []; // {color_name, swatch_data, qty, id}
var cropperInstance = null;
var colorItemIdCounter = 0;

function initCropperUpload(){
  var openBtn = document.getElementById('openCropperBtn');
  var fileInput = document.getElementById('cropperFileInput');
  var modal = document.getElementById('cropperModal');
  var img = document.getElementById('cropperImage');
  var colorName = document.getElementById('cropperColorName');
  var confirmBtn = document.getElementById('cropperConfirmBtn');
  var closeBtn = document.getElementById('closeCropperBtn');
  if(!openBtn || !fileInput) return;

  // Open file picker
  openBtn.addEventListener('click', function(){
    fileInput.click();
  });

  // File selected
  fileInput.addEventListener('change', function(){
    var file = this.files[0];
    if(!file) return;
    var reader = new FileReader();
    reader.onload = function(e){
      img.src = e.target.result;
      modal.style.display = 'flex';
      // Destroy previous cropper
      if(cropperInstance) cropperInstance.destroy();
      // Initialize cropper on next frame after image loads
      img.onload = function(){
        cropperInstance = new Cropper(img, {
          aspectRatio: NaN,
          viewMode: 1,
          autoCropArea: 0.8,
          background: false
        });
        confirmBtn.disabled = false;
        colorName.value = '';
        colorName.focus();
      };
    };
    reader.readAsDataURL(file);
    this.value = '';
  });

  // Confirm crop
  confirmBtn.addEventListener('click', function(){
    if(!cropperInstance) return;
    var name = colorName.value.trim();
    if(!name){
      colorName.focus();
      colorName.style.borderColor = '#c41e3a';
      setTimeout(function(){ colorName.style.borderColor = ''; }, 1500);
      return;
    }
    var canvas = cropperInstance.getCroppedCanvas({
      width: 200,
      height: 200
    });
    var dataUrl = canvas.toDataURL('image/png');
    addColorItem(name, dataUrl);
    closeCropper();
    // Flash success feedback
    var btn = openBtn;
    var orig = btn.textContent;
    btn.textContent = '✓ 已添加';
    btn.style.color = '#4caf50';
    setTimeout(function(){ btn.textContent = orig; btn.style.color = ''; }, 1500);
  });

  // Close modal
  function closeCropper(){
    modal.style.display = 'none';
    if(cropperInstance){ cropperInstance.destroy(); cropperInstance = null; }
    confirmBtn.disabled = true;
  }
  if(closeBtn) closeBtn.addEventListener('click', closeCropper);
  modal.addEventListener('click', function(e){
    if(e.target === modal) closeCropper();
  });
}

function addColorItem(name, swatchData){
  var list = document.getElementById('colorItemsList');
  if(!list) return;
  var id = ++colorItemIdCounter;
  colorItems.push({color_name: name, swatch_data: swatchData, qty: 1, id: id});

  var div = document.createElement('div');
  div.className = 'color-item';
  div.dataset.id = id;
  div.innerHTML =
    '<img class="ci-swatch" src="' + swatchData + '" alt="">' +
    '<span class="ci-name">' + escapeHtml(name) + '</span>' +
    '<button type="button" class="ci-qty-btn" data-action="dec">−</button>' +
    '<span class="ci-qty">1</span>' +
    '<button type="button" class="ci-qty-btn" data-action="inc">+</button>' +
    '<button type="button" class="ci-del" data-action="del">✕</button>';
  div.addEventListener('click', function(e){
    var target = e.target;
    var action = target.getAttribute('data-action');
    var itemId = parseInt(div.dataset.id);
    var item = colorItems.find(function(i){ return i.id === itemId; });
    if(!item) return;
    if(action === 'inc'){
      item.qty++;
      div.querySelector('.ci-qty').textContent = item.qty;
    } else if(action === 'dec'){
      if(item.qty > 1){
        item.qty--;
        div.querySelector('.ci-qty').textContent = item.qty;
      }
    } else if(action === 'del'){
      colorItems = colorItems.filter(function(i){ return i.id !== itemId; });
      div.remove();
    }
    updateOrderSummary();
  });
  list.appendChild(div);
  updateOrderSummary();
}

function initPresetColors(){
  document.querySelectorAll('#presetSwatches .swatch-circle').forEach(function(el){
    el.addEventListener('click', function(){
      var name = this.getAttribute('data-color') || '自定义';
      // Generate a small swatch image from the CSS background color
      var bg = this.style.backgroundColor || '#ddd';
      var canvas = document.createElement('canvas');
      canvas.width = 100; canvas.height = 100;
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, 100, 100);
      var dataUrl = canvas.toDataURL('image/png');
      addColorItem(name, dataUrl);
    });
  });
}

function initCustomSizeToggle(){
  var btn = document.getElementById('customSizeBtn');
  var block = document.getElementById('customSizeBlock');
  var input = document.getElementById('customSizeInput');
  var sizeField = document.getElementById('sizeField');
  if(!btn || !block) return;

  btn.addEventListener('click', function(){
    var isActive = block.style.display !== 'none';
    block.style.display = isActive ? 'none' : 'block';
    btn.classList.toggle('active', !isActive);
    if(!isActive){
      // Custom mode: clear the hidden size and let textarea value be used
      sizeField.value = '';
      input.focus();
    } else {
      // Back to standard size
      var activeSize = document.querySelector('.size-grid .size-btn.active:not(.custom)');
      sizeField.value = activeSize ? activeSize.getAttribute('data-size') : 'M';
    }
  });
}

// Also update the hidden size field when standard size buttons are clicked
function initSizeFieldSync(){
  document.querySelectorAll('.size-grid .size-btn').forEach(function(btn){
    if(btn.id === 'customSizeBtn') return;
    btn.addEventListener('click', function(){
      var sizeField = document.getElementById('sizeField');
      if(sizeField) sizeField.value = this.getAttribute('data-size') || this.textContent.trim();
    });
  });
}

function updateOrderSummary(){
  var sub = document.getElementById('orderSub');
  if(!sub) return;
  var total = 0;
  colorItems.forEach(function(item){ total += item.qty; });
  sub.textContent = '· ' + total + '件';
}

function initFormSubmit(){
  var form = document.getElementById('orderForm');
  if(!form) return;
  form.addEventListener('submit', function(e){
    var itemsField = document.getElementById('itemsField');
    if(!itemsField) return;

    // Handle custom size
    var customBlock = document.getElementById('customSizeBlock');
    var sizeField = document.getElementById('sizeField');
    if(customBlock && customBlock.style.display !== 'none'){
      var customInput = document.getElementById('customSizeInput');
      if(customInput && customInput.value.trim()){
        sizeField.value = customInput.value.trim();
      }
    }

    if(colorItems.length === 0){
      e.preventDefault();
      alert('请至少添加一个花色');
      return;
    }

    // Serialize items (strip internal id, keep only what backend expects)
    var payload = colorItems.map(function(item){
      return {
        color_name: item.color_name,
        swatch_data: item.swatch_data,
        qty: item.qty
      };
    });
    itemsField.value = JSON.stringify(payload);

    // Disable submit button to prevent double submit
    var submitBtn = form.querySelector('.order-btn');
    if(submitBtn){
      submitBtn.disabled = true;
      submitBtn.textContent = '提交中…';
    }
  });
}

function escapeHtml(str){
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

// ---- Init on DOM ready ----
document.addEventListener('DOMContentLoaded',function(){
  initCarousels();
  initQty();
  initSize();
  initSwatches();
  initOrderForm();
  initConfirm();
  initCropperUpload();
  initPresetColors();
  initCustomSizeToggle();
  initSizeFieldSync();
  initFormSubmit();
});

})();
