// LUNA ATELIER — App JS
(function(){
'use strict';

// ---- Image Viewer (Fullscreen overlay for carousel images) ----
var viewerActive = false;
var viewerTrackEl = null;
var viewerSlides = null;
var viewerIdx = 0;
var viewerStartX = 0;
var viewerStartY = 0;
var viewerOffsetX = 0;
var viewerOffsetY = 0;
var viewerDragging = false;
var viewerScale = 1;
var viewerLastDist = 0;

function openViewer(clickedSlide, slides, currentIdx){
  if(viewerActive) return;
  viewerActive = true;
  viewerSlides = slides;
  viewerIdx = currentIdx;
  viewerScale = 1;

  // Create overlay
  var overlay = document.createElement('div');
  overlay.id = 'imageViewerOverlay';
  overlay.style.cssText = 'position:fixed;inset:0;background:#000;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;touch-action:none;overflow:hidden;';

  // Close button
  var closeBtn = document.createElement('button');
  closeBtn.textContent = '✕';
  closeBtn.style.cssText = 'position:absolute;top:16px;right:16px;width:36px;height:36px;border:none;background:rgba(255,255,255,.15);color:#fff;font-size:18px;border-radius:50%;cursor:pointer;z-index:10;display:flex;align-items:center;justify-content:center;';
  overlay.appendChild(closeBtn);

  // Counter
  var counter = document.createElement('div');
  counter.id = 'viewerCounter';
  counter.style.cssText = 'position:absolute;top:20px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.6);font-size:12px;z-index:10;';
  overlay.appendChild(counter);

  // Image wrapper for pan/zoom
  var wrapper = document.createElement('div');
  wrapper.id = 'viewerWrapper';
  wrapper.style.cssText = 'width:100%;height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;';

  var img = document.createElement('img');
  img.id = 'viewerImage';
  img.style.cssText = 'max-width:100%;max-height:100%;object-fit:contain;transition:transform .2s;cursor:grab;user-select:none;-webkit-user-select:none;';
  wrapper.appendChild(img);

  // Arrow buttons
  var prevBtn = document.createElement('button');
  prevBtn.textContent = '‹';
  prevBtn.style.cssText = 'position:absolute;left:10px;top:50%;transform:translateY(-50%);width:36px;height:36px;border:none;background:rgba(255,255,255,.12);color:#fff;font-size:22px;border-radius:50%;cursor:pointer;z-index:5;display:flex;align-items:center;justify-content:center;';
  var nextBtn = document.createElement('button');
  nextBtn.textContent = '›';
  nextBtn.style.cssText = 'position:absolute;right:10px;top:50%;transform:translateY(-50%);width:36px;height:36px;border:none;background:rgba(255,255,255,.12);color:#fff;font-size:22px;border-radius:50%;cursor:pointer;z-index:5;display:flex;align-items:center;justify-content:center;';
  overlay.appendChild(prevBtn);
  overlay.appendChild(nextBtn);

  overlay.appendChild(wrapper);
  document.body.appendChild(overlay);

  function updateViewerImage(){
    var slideImgs = viewerSlides[viewerIdx].querySelectorAll('img');
    if(slideImgs.length > 0){
      img.src = slideImgs[0].src;
    }
    counter.textContent = (viewerIdx + 1) + ' / ' + viewerSlides.length;
    viewerScale = 1;
    img.style.transform = 'scale(1) translate(0, 0)';
    viewerOffsetX = 0;
    viewerOffsetY = 0;
  }

  function closeViewer(){
    viewerActive = false;
    var o = document.getElementById('imageViewerOverlay');
    if(o) o.remove();
  }

  function goToPrev(){
    viewerIdx = (viewerIdx - 1 + viewerSlides.length) % viewerSlides.length;
    updateViewerImage();
  }

  function goToNext(){
    viewerIdx = (viewerIdx + 1) % viewerSlides.length;
    updateViewerImage();
  }

  updateViewerImage();

  closeBtn.addEventListener('click', closeViewer);
  overlay.addEventListener('click', function(e){
    if(e.target === overlay) closeViewer();
  });
  prevBtn.addEventListener('click', function(e){ e.stopPropagation(); goToPrev(); });
  nextBtn.addEventListener('click', function(e){ e.stopPropagation(); goToNext(); });

  // Touch events for pan, zoom, swipe
  var touchStartX = 0, touchStartY = 0, touchStartOffsetX = 0, touchStartOffsetY = 0;
  var touchStartScale = 1;

  overlay.addEventListener('touchstart', function(e){
    if(e.touches.length === 1){
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      touchStartOffsetX = viewerOffsetX;
      touchStartOffsetY = viewerOffsetY;
      touchStartScale = viewerScale;
      viewerDragging = false;
      viewerLastDist = 0;
    } else if(e.touches.length === 2){
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      viewerLastDist = Math.sqrt(dx*dx + dy*dy);
      touchStartScale = viewerScale;
    }
  }, {passive:true});

  overlay.addEventListener('touchmove', function(e){
    e.preventDefault();
    if(e.touches.length === 1 && viewerLastDist === 0){
      var dx = e.touches[0].clientX - touchStartX;
      var dy = e.touches[0].clientY - touchStartY;
      if(!viewerDragging && (Math.abs(dx) > 5 || Math.abs(dy) > 5)){
        viewerDragging = true;
        img.style.cursor = 'grabbing';
      }
      if(viewerDragging){
        viewerOffsetX = touchStartOffsetX + dx;
        viewerOffsetY = touchStartOffsetY + dy;
        img.style.transform = 'scale(' + viewerScale + ') translate(' + (viewerOffsetX/viewerScale) + 'px,' + (viewerOffsetY/viewerScale) + 'px)';
      }
    } else if(e.touches.length === 2){
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      var dist = Math.sqrt(dx*dx + dy*dy);
      if(viewerLastDist > 0){
        viewerScale = Math.max(0.5, Math.min(5, touchStartScale * (dist / viewerLastDist)));
        img.style.transform = 'scale(' + viewerScale + ') translate(' + (viewerOffsetX/viewerScale) + 'px,' + (viewerOffsetY/viewerScale) + 'px)';
      }
    }
  }, {passive:false});

  overlay.addEventListener('touchend', function(e){
    if(e.touches.length === 0){
      if(!viewerDragging && viewerLastDist === 0){
        // If no drag, check for horizontal swipe
        var dx = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0].clientX - touchStartX : 0;
        if(Math.abs(dx) > 60 && viewerScale <= 1){
          if(dx > 0) goToPrev();
          else goToNext();
        }
      }
      viewerDragging = false;
      viewerLastDist = 0;
      if(img) img.style.cursor = 'grab';
      // If scale < 1, snap back
      if(viewerScale < 0.5) viewerScale = 0.5;
      img.style.transform = 'scale(' + viewerScale + ') translate(' + (viewerOffsetX/viewerScale) + 'px,' + (viewerOffsetY/viewerScale) + 'px)';
    } else if(e.touches.length === 1){
      viewerLastDist = 0;
    }
  }, {passive:true});

  // Mouse drag
  var mouseDown = false;
  var mouseStartX = 0, mouseStartY = 0;
  var mouseOffsetX = 0, mouseOffsetY = 0;

  img.addEventListener('mousedown', function(e){
    e.preventDefault();
    mouseDown = true;
    mouseStartX = e.clientX;
    mouseStartY = e.clientY;
    mouseOffsetX = viewerOffsetX;
    mouseOffsetY = viewerOffsetY;
    img.style.cursor = 'grabbing';
  });

  document.addEventListener('mousemove', function(e){
    if(!mouseDown) return;
    var dx = e.clientX - mouseStartX;
    var dy = e.clientY - mouseStartY;
    viewerOffsetX = mouseOffsetX + dx;
    viewerOffsetY = mouseOffsetY + dy;
    img.style.transform = 'scale(' + viewerScale + ') translate(' + (viewerOffsetX/viewerScale) + 'px,' + (viewerOffsetY/viewerScale) + 'px)';
  });

  document.addEventListener('mouseup', function(e){
    if(!mouseDown) return;
    mouseDown = false;
    img.style.cursor = 'grab';
    // Check for swipe (only at scale=1 with minimal vertical move)
    var dx = e.clientX - mouseStartX;
    var dy = e.clientY - mouseStartY;
    if(Math.abs(dx) > 60 && Math.abs(dy) < 40 && viewerScale <= 1.1){
      if(dx > 0) goToPrev();
      else goToNext();
    }
  });

  // Double-click to zoom
  img.addEventListener('dblclick', function(e){
    e.preventDefault();
    if(viewerScale > 1.5){
      viewerScale = 1;
      viewerOffsetX = 0;
      viewerOffsetY = 0;
    } else {
      viewerScale = 2.5;
      // Zoom towards cursor position
      var rect = img.getBoundingClientRect();
      viewerOffsetX = (e.clientX - rect.left - rect.width/2) * (1 - 1/viewerScale);
      viewerOffsetY = (e.clientY - rect.top - rect.height/2) * (1 - 1/viewerScale);
    }
    img.style.transform = 'scale(' + viewerScale + ') translate(' + (viewerOffsetX/viewerScale) + 'px,' + (viewerOffsetY/viewerScale) + 'px)';
  });

  // Keyboard nav
  document.addEventListener('keydown', viewerKeyHandler = function(e){
    if(!viewerActive) return;
    if(e.key === 'Escape') closeViewer();
    if(e.key === 'ArrowLeft') goToPrev();
    if(e.key === 'ArrowRight') goToNext();
  });
}

// ---- Touch Carousel (Seamless Infinite Loop via Clone Method) ----
function initCarousels(){
  document.querySelectorAll('.pdp-carousel').forEach(function(wrap){
    var track = wrap.querySelector('.track');
    if(!track) return;
    var origSlides = Array.from(track.children);
    var N = origSlides.length;
    if(N < 2) return;

    // --- Clone setup: N+2 slides ---
    // Clone last slide → insert before first; clone first slide → append after last
    var firstClone = origSlides[0].cloneNode(true);
    var lastClone = origSlides[N-1].cloneNode(true);
    track.insertBefore(lastClone, origSlides[0]);
    track.appendChild(firstClone);

    // All slides now (0=clone of last, 1..N=originals, N+1=clone of first)
    var idx = 1;        // start at first real slide
    var startX = 0;
    var currentX = 0;
    var dragging = false;
    var animating = false;

    // --- Build dots (only for N real slides) ---
    var dotsContainer = wrap.querySelector('.pdp-dots');
    if(dotsContainer){
      dotsContainer.innerHTML = '';
      for(var di=0; di<N; di++){
        var dot = document.createElement('span');
        if(di === 0) dot.className = 'active';
        dotsContainer.appendChild(dot);
      }
    }

    // --- Position track at idx (no animation) ---
    function render(animate){
      if(animate){
        track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
        animating = true;
      } else {
        track.style.transition = 'none';
      }
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      // Update dots (real slide index = idx-1 when idx in [1..N])
      var realIdx = idx - 1;
      var dots = wrap.querySelectorAll('.pdp-dots span');
      dots.forEach(function(d,j){ d.classList.toggle('active', j === realIdx); });
    }

    // --- Jump correction on transitionend ---
    function onTransitionEnd(){
      animating = false;
      // If at clone of last (idx=0): jump to real last (idx=N)
      if(idx === 0){
        idx = N;
        render(false);
      }
      // If at clone of first (idx=N+1): jump to real first (idx=1)
      else if(idx === N + 1){
        idx = 1;
        render(false);
      }
    }
    track.addEventListener('transitionend', onTransitionEnd);

    // --- Initial position
    render(false);

    // --- Click image → open fullscreen viewer ---
    var allSlides = Array.from(track.children);
    origSlides.forEach(function(slide, i){
      var slideImg = slide.querySelector('img');
      if(slideImg){
        slideImg.style.cursor = 'zoom-in';
        slideImg.addEventListener('click', function(e){
          e.stopPropagation();
          openViewer(slide, origSlides, i);
        });
      }
    });

    // --- Arrow navigation ---
    function slide(dir){
      if(animating) return;
      idx += dir;
      render(true);
    }

    var prev = wrap.querySelector('.pdp-arrow-prev');
    var next = wrap.querySelector('.pdp-arrow-next');
    if(prev) prev.addEventListener('click',function(e){e.stopPropagation();slide(-1);});
    if(next) next.addEventListener('click',function(e){e.stopPropagation();slide(1);});

    // --- Touch events ---
    track.addEventListener('touchstart',function(e){
      if(animating) return;
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
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.3){
        idx += (diff < 0 ? 1 : -1);
        render(true);
      } else {
        render(false);
      }
    }, {passive:true});

    // --- Mouse drag (desktop) ---
    track.addEventListener('mousedown',function(e){
      if(animating) return;
      startX = e.clientX;
      currentX = startX;
      dragging = true;
      track.style.transition = 'none';
    });
    track.addEventListener('mousemove',function(e){
      if(!dragging) return;
      currentX = e.clientX;
      var diff = currentX - startX;
      track.style.transform = 'translateX(' + (-idx * 100 + diff / track.offsetWidth * 100) + '%)';
    });
    track.addEventListener('mouseup',function(){
      if(!dragging) return;
      dragging = false;
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.3){
        idx += (diff < 0 ? 1 : -1);
        render(true);
      } else {
        render(false);
      }
    });
    track.addEventListener('mouseleave',function(){
      if(!dragging) return;
      dragging = false;
      render(false);
    });
  });
}

// ---- Qty Stepper (kept for compatibility) ----
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

// ---- Swatch Select (preset colors → add to order) ----
function initSwatches(){
  document.querySelectorAll('.swatch-row').forEach(function(row){
    row.addEventListener('click',function(e){
      var sw = e.target.closest('.swatch-circle');
      if(!sw) return;
      // Only handle preset swatches (have data-color attribute)
      var colorName = sw.getAttribute('data-color');
      if(!colorName) return;
      // Toggle active visual
      row.querySelectorAll('.swatch-circle').forEach(function(s){ s.classList.remove('active'); });
      sw.classList.add('active');
      // Check if this color is already in colorItems — skip if duplicate
      var alreadyAdded = colorItems.some(function(item){
        return item.color_name === colorName;
      });
      if(alreadyAdded) return;
      // Generate a 200x200 solid-color swatch image
      var bg = sw.style.backgroundColor || '#ddd';
      var canvas = document.createElement('canvas');
      canvas.width = 200; canvas.height = 200;
      var ctx = canvas.getContext('2d');
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, 200, 200);
      var dataUrl = canvas.toDataURL('image/png');
      addColorItem(colorName, dataUrl);
      // Update hidden input for backward compatibility
      var parentRow = row.closest('.opt-block');
      var hidden = parentRow ? parentRow.querySelector('input[name="color"]') : null;
      if(hidden) hidden.value = colorName;
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
var colorItems = []; // {color_name, swatch_data, size_quantities: {}, id}
var cropperInstance = null;
var colorItemIdCounter = 0;
var SIZES = ['XS','S','M','L','XL','2XL','3XL'];

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
    addColorItem('', dataUrl);
    closeCropper();
    // Flash success feedback
    var btn = openBtn;
    btn.textContent = '✓ 已添加';
    btn.style.backgroundColor = '#4caf50';
    btn.style.color = '#fff';
    btn.style.borderColor = '#4caf50';
    setTimeout(function(){ 
      btn.textContent = '📷 上传花版'; 
      btn.style.backgroundColor = '';
      btn.style.color = '#999';
      btn.style.borderColor = '#ddd';
    }, 1500);
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
  
  // Initialize size_quantities with all zeros
  var sizeQtys = {};
  SIZES.forEach(function(s){ sizeQtys[s] = 0; });
  
  colorItems.push({color_name: name, swatch_data: swatchData, size_quantities: sizeQtys, id: id});

  var div = document.createElement('div');
  div.className = 'color-item';
  div.dataset.id = id;

  var sizeMatrixHtml = '';
  SIZES.forEach(function(s){
    sizeMatrixHtml += '<div class="sm-cell">' +
      '<span class="sm-label">' + s + '</span>' +
      '<input type="number" class="size-qty-input" data-size="' + s + '" value="0" min="0">' +
      '</div>';
  });

  div.innerHTML =
    '<img class="ci-swatch" src="' + swatchData + '" alt="">' +
    '<span class="ci-name" contenteditable="true">' + (name || '未命名') + '</span>' +
    '<button type="button" class="ci-del" data-action="del">&times;</button>' +
    '<div class="size-matrix">' +
      sizeMatrixHtml +
    '</div>' +
    '<div class="quick-fill-row">' +
      '<span class="qf-label">快捷:</span>' +
      '<button type="button" class="quick-fill-btn" data-qty="5">5</button>' +
      '<button type="button" class="quick-fill-btn" data-qty="10">10</button>' +
      '<button type="button" class="quick-fill-btn" data-qty="15">15</button>' +
      '<button type="button" class="quick-fill-btn" data-qty="20">20</button>' +
    '</div>' +
    '<div class="custom-size-row">' +
      '<span style="font-size:10px;color:#aaa;">定制尺码:</span>' +
      '<input type="text" class="ci-custom-size" placeholder="如: 28码">' +
    '</div>' +
    '<div class="ci-total">🔴 合计: <strong class="ci-item-total">0</strong>件</div>';

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

  // Size input change handler
  div.querySelectorAll('.size-qty-input').forEach(function(inp){
    inp.addEventListener('input', function(){
      var item = colorItems.find(function(i){ return i.id === id; });
      if(!item) return;
      var sz = this.dataset.size;
      var val = parseInt(this.value) || 0;
      if(val < 0) val = 0;
      item.size_quantities[sz] = val;
      updateColorItemTotal(div, item);
      updateOrderSummary();
    });
    // Track focus for quick-fill
    inp.addEventListener('focus', function(){
      // Remove focused class from all inputs
      div.querySelectorAll('.size-qty-input').forEach(function(i){ i.classList.remove('focused-input'); });
      this.classList.add('focused-input');
    });
  });

  // Delete handler
  div.addEventListener('click', function(e){
    var target = e.target;
    var action = target.getAttribute('data-action');
    var itemId = parseInt(div.dataset.id);
    var item = colorItems.find(function(i){ return i.id === itemId; });
    if(!item) return;
    
    if(action === 'del'){
      colorItems = colorItems.filter(function(i){ return i.id !== itemId; });
      div.remove();
      updateOrderSummary();
      return;
    }

    // Quick fill buttons — fill the focused input
    var qfBtn = target.closest('.quick-fill-btn');
    if(qfBtn){
      var focusedInput = div.querySelector('.size-qty-input.focused-input');
      if(focusedInput){
        focusedInput.value = qfBtn.dataset.qty;
        // Trigger input event
        var evt = new Event('input', {bubbles: true});
        focusedInput.dispatchEvent(evt);
      } else {
        // If none focused, fill the first non-zero? No, fill M
        var mInput = div.querySelector('.size-qty-input[data-size="M"]');
        if(mInput){
          mInput.value = qfBtn.dataset.qty;
          mInput.classList.add('focused-input');
          var evt = new Event('input', {bubbles: true});
          mInput.dispatchEvent(evt);
        }
      }
    }
  });

  list.appendChild(div);
  updateColorItemTotal(div, colorItems[colorItems.length - 1]);
  updateOrderSummary();
}

function updateColorItemTotal(div, item){
  var totalEl = div.querySelector('.ci-item-total');
  if(!totalEl || !item) return;
  var total = 0;
  SIZES.forEach(function(s){
    total += item.size_quantities[s] || 0;
  });
  totalEl.textContent = total;
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
  colorItems.forEach(function(item){
    SIZES.forEach(function(s){
      total += item.size_quantities[s] || 0;
    });
  });
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
        size_quantities: item.size_quantities
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
  initCustomSizeToggle();
  initSizeFieldSync();
  initFormSubmit();
  initInlineRename();
});

})();
