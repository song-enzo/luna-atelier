// LUNA ATELIER — App JS
(function(){
'use strict';

// ---- Touch Carousel (Non-looping, bounce at ends) ----
function initCarousels(){
  document.querySelectorAll('.pdp-carousel').forEach(function(wrap){
    var track = wrap.querySelector('.track');
    if(!track) return;
    var slides = track.children;
    if(slides.length < 2) return;

    var idx = 0, startX = 0, currentX = 0, dragging = false;

    function goTo(i, animate){
      // Clamp to valid range — no wrapping
      if(i < 0) i = 0;
      if(i >= slides.length) i = slides.length - 1;
      idx = i;
      if(!animate) track.style.transition = 'none';
      else track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      var dots = wrap.querySelectorAll('.pdp-dots span');
      dots.forEach(function(d,j){ d.classList.toggle('active',j===idx); });
    }

    function slide(dir){
      var newIdx = idx + dir;
      // Bounce at ends — if at edge, spring back
      if(newIdx < 0 || newIdx >= slides.length){
        // Quick bounce animation
        track.style.transition = 'transform .15s cubic-bezier(.25,.46,.45,.94)';
        var bounceDir = dir < 0 ? 20 : -20;
        track.style.transform = 'translateX(' + (-idx * 100 + bounceDir) + '%)';
        setTimeout(function(){
          track.style.transition = 'transform .25s cubic-bezier(.25,.46,.45,.94)';
          track.style.transform = 'translateX(-' + (idx * 100) + '%)';
        }, 150);
        return;
      }
      goTo(newIdx, true);
    }

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
      // Apply resistance at edges
      var resistance = 1;
      if((idx === 0 && diff > 0) || (idx === slides.length - 1 && diff < 0)){
        resistance = 0.3; // Bouncy resistance at edges
      }
      var pct = -idx * 100 + (diff / track.offsetWidth * 100 * resistance);
      track.style.transform = 'translateX(' + pct + '%)';
    }, {passive:true});

    track.addEventListener('touchend',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.2){
        // Only slide if not at edge in the direction of movement
        var direction = diff < 0 ? 1 : -1;
        var newIdx = idx + direction;
        if(newIdx >= 0 && newIdx < slides.length){
          idx = newIdx;
          track.style.transform = 'translateX(-' + (idx * 100) + '%)';
        } else {
          // Bounce back to current
          track.style.transform = 'translateX(-' + (idx * 100) + '%)';
        }
      } else {
        track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      }
      var dots = wrap.querySelectorAll('.pdp-dots span');
      dots.forEach(function(d,j){ d.classList.toggle('active',j===idx); });
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
      var resistance = 1;
      if((idx === 0 && diff > 0) || (idx === slides.length - 1 && diff < 0)){
        resistance = 0.3;
      }
      track.style.transform = 'translateX(' + (-idx * 100 + diff/track.offsetWidth*100*resistance) + '%)';
    });
    track.addEventListener('mouseup',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.2){
        var direction = diff < 0 ? 1 : -1;
        var newIdx = idx + direction;
        if(newIdx >= 0 && newIdx < slides.length){
          idx = newIdx;
        }
      }
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      var dots = wrap.querySelectorAll('.pdp-dots span');
      dots.forEach(function(d,j){ d.classList.toggle('active',j===idx); });
    });
    track.addEventListener('mouseleave',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
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
      };
    };
    reader.readAsDataURL(file);
    this.value = '';
  });

  // Confirm crop — NO color name required, just crop and add
  confirmBtn.addEventListener('click', function(){
    if(!cropperInstance) return;
    var canvas = cropperInstance.getCroppedCanvas({
      width: 200,
      height: 200
    });
    var dataUrl = canvas.toDataURL('image/png');
    // Use empty name — user can edit later
    addColorItem('', dataUrl);
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
    '<span class="ci-name" contenteditable="true">' + (name || '未命名') + '</span>' +
    '<div style="display:flex;align-items:center;gap:4px;">' +
    '<button type="button" class="ci-qty-btn" data-action="dec">&minus;</button>' +
    '<span class="ci-qty">1</span>' +
    '<button type="button" class="ci-qty-btn" data-action="inc">+</button>' +
    '</div>' +
    '<div class="qty-presets" style="display:flex;gap:2px;">' +
    '<button type="button" class="qty-preset-btn" data-qty="1">1</button>' +
    '<button type="button" class="qty-preset-btn" data-qty="2">2</button>' +
    '<button type="button" class="qty-preset-btn" data-qty="3">3</button>' +
    '<button type="button" class="qty-preset-btn" data-qty="5">5</button>' +
    '<button type="button" class="qty-preset-btn" data-qty="10">10</button>' +
    '</div>' +
    '<button type="button" class="ci-del" data-action="del">&times;</button>';
  
  // Allow inline editing of name
  var nameSpan = div.querySelector('.ci-name');
  nameSpan.addEventListener('blur', function(){
    var item = colorItems.find(function(i){ return i.id === id; });
    if(item) item.color_name = this.textContent.trim();
  });
  nameSpan.addEventListener('keydown', function(e){
    if(e.key === 'Enter'){
      e.preventDefault();
      this.blur();
    }
  });

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
    // Handle qty preset buttons
    var qtyPreset = target.closest('.qty-preset-btn');
    if(qtyPreset){
      var presetVal = parseInt(qtyPreset.dataset.qty);
      if(presetVal > 0){
        item.qty = presetVal;
        div.querySelector('.ci-qty').textContent = presetVal;
      }
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
      sizeField.value = '';
      input.focus();
    } else {
      var activeSize = document.querySelector('.size-grid .size-btn.active:not(.custom)');
      sizeField.value = activeSize ? activeSize.getAttribute('data-size') : 'M';
    }
  });
}

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

    var payload = colorItems.map(function(item){
      return {
        color_name: item.color_name,
        swatch_data: item.swatch_data,
        qty: item.qty
      };
    });
    itemsField.value = JSON.stringify(payload);

    var submitBtn = form.querySelector('.order-btn');
    if(submitBtn){
      submitBtn.disabled = true;
      submitBtn.textContent = '提交中…';
    }
  });
}

// ---- Inline Style Name Edit (admin) ----
function initInlineRename(){
  document.querySelectorAll('.style-name-edit').forEach(function(el){
    el.addEventListener('dblclick', function(){
      var currentName = this.textContent.trim();
      var id = this.dataset.id;
      var input = document.createElement('input');
      input.type = 'text';
      input.value = currentName;
      input.className = 'inline-rename-input';
      input.style.cssText = 'width:100%;padding:4px 6px;border:1px solid #111;font-size:12px;font-family:inherit;border-radius:2px;';
      this.textContent = '';
      this.appendChild(input);
      input.focus();
      input.select();

      function save(){
        var newName = input.value.trim();
        if(newName && newName !== currentName){
          fetch('/admin/style/' + id + '/rename', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: newName})
          })
          .then(function(r){ return r.json(); })
          .then(function(data){
            el.textContent = data.name;
          })
          .catch(function(){
            el.textContent = currentName;
          });
        } else {
          el.textContent = currentName;
        }
      }

      input.addEventListener('blur', save);
      input.addEventListener('keydown', function(e){
        if(e.key === 'Enter'){ e.preventDefault(); this.blur(); }
        if(e.key === 'Escape'){ el.textContent = currentName; }
      });
    });
  });
}

// ---- Qty Multi-Select (new_order: clickable qty options) ----
function initQtyMultiSelect(){
  document.querySelectorAll('.qty-multi-options').forEach(function(container){
    container.addEventListener('click', function(e){
      var btn = e.target.closest('.qty-option-btn');
      if(!btn) return;
      btn.classList.toggle('selected');
    });
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
  initInlineRename();
  initQtyMultiSelect();
});

})();
