  // ── Theme ──────────────────────────────────────────────
  function getTheme() { return localStorage.getItem('sv-theme') || 'dark'; }
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.getElementById('themeIcon');
    const label = document.getElementById('themeLabel');
    if (theme === 'dark') {
      icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
      label.textContent = 'Light Mode';
    } else {
      icon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
      label.textContent = 'Dark Mode';
    }
  }
  function toggleTheme() {
    const next = getTheme() === 'dark' ? 'light' : 'dark';
    localStorage.setItem('sv-theme', next);
    applyTheme(next);
  }
  applyTheme(getTheme());

  // ── Sidebar (mobile) ──────────────────────────────────
  function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('show');
  }

  // ── Tab switching ─────────────────────────────────────
  const tabNames = { image: 'Image Detection', video: 'Video Detection', live: 'Live Camera', register: 'Register Workers' };
  function switchTab(tab, navEl) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    if (navEl) navEl.classList.add('active');
    document.getElementById('breadcrumbCurrent').textContent = tabNames[tab] || tab;
    // Only show results pane if this tab has results
    var wrap = document.querySelector('.content-wrap');
    if (wrap) {
      if (window._resultTab && tab === window._resultTab) {
        wrap.classList.add('has-result');
      } else {
        wrap.classList.remove('has-result');
      }
    }
    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }

  // ── Image Upload ──────────────────────────────────────
  const imageFileInput = document.getElementById('imageFileInput');
  const imageFileName = document.getElementById('imageFileName');
  const imageSubmitBtn = document.getElementById('imageSubmitBtn');
  const imageDropArea = document.getElementById('imageDropArea');
  const imageForm = document.getElementById('imageForm');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');

  imageFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
      imageFileName.textContent = this.files[0].name;
      imageSubmitBtn.disabled = false;
      imageDropArea.classList.add('has-file');
      const reader = new FileReader();
      reader.onload = e => { imagePreview.src = e.target.result; imagePreviewContainer.classList.add('show'); };
      reader.readAsDataURL(this.files[0]);
    }
  });
  imageForm.addEventListener('submit', function() { imageSubmitBtn.classList.add('loading'); imageSubmitBtn.textContent = 'Analyzing'; });

  // ── Video Upload ──────────────────────────────────────
  const videoFileInput = document.getElementById('videoFileInput');
  const videoFileName = document.getElementById('videoFileName');
  const videoSubmitBtn = document.getElementById('videoSubmitBtn');
  const videoDropArea = document.getElementById('videoDropArea');
  const videoForm = document.getElementById('videoForm');
  const videoPreviewContainer = document.getElementById('videoPreviewContainer');
  const videoPreview = document.getElementById('videoPreview');

  videoFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
      const file = this.files[0];
      videoFileName.textContent = file.name + ' (' + (file.size / (1024*1024)).toFixed(1) + ' MB)';
      videoSubmitBtn.disabled = false;
      videoDropArea.classList.add('has-file');
      const url = URL.createObjectURL(file);
      videoPreview.src = url;
      videoPreviewContainer.classList.add('show');
    }
  });
  videoForm.addEventListener('submit', function() { videoSubmitBtn.classList.add('loading'); videoSubmitBtn.textContent = 'Analyzing video...'; });

  // ── Drag & Drop ───────────────────────────────────────
  function setupDragDrop(dropArea, fileInput) {
    ['dragover','dragenter'].forEach(e => {
      dropArea.addEventListener(e, ev => { ev.preventDefault(); dropArea.classList.add('dragover'); });
    });
    ['dragleave','drop'].forEach(e => {
      dropArea.addEventListener(e, ev => { ev.preventDefault(); dropArea.classList.remove('dragover'); });
    });
    dropArea.addEventListener('drop', ev => {
      ev.preventDefault();
      fileInput.files = ev.dataTransfer.files;
      fileInput.dispatchEvent(new Event('change'));
    });
  }
  setupDragDrop(imageDropArea, imageFileInput);
  setupDragDrop(videoDropArea, videoFileInput);

  // ── Live Camera ───────────────────────────────────────
  let liveStatusInterval = null;

  function startLive() {
    // Release browser webcam first (Register tab) so OpenCV can access it
    regStopCamera();
    fetch('/live/start', {method: 'POST'}).then(r => r.json()).then(data => {
      if (data.status === 'ok' || data.status === 'already_running') {
        document.getElementById('liveFeedContainer').style.display = 'block';
        document.getElementById('liveFeed').src = '/live_feed?' + Date.now();
        document.getElementById('startCamBtn').disabled = true;
        document.getElementById('startCamBtn').style.background = 'var(--border-color)';
        document.getElementById('startCamBtn').style.color = 'var(--text-muted)';
        document.getElementById('stopCamBtn').disabled = false;
        document.getElementById('stopCamBtn').style.background = 'var(--danger)';
        document.getElementById('stopCamBtn').style.color = '#fff';
        liveStatusInterval = setInterval(updateLiveStatus, 500);
      } else {
        alert('Failed to start camera: ' + (data.message || 'Unknown error'));
      }
    }).catch(e => alert('Error: ' + e));
  }

  function stopLive() {
    // Clear polling immediately, don't wait for server response
    if (liveStatusInterval) { clearInterval(liveStatusInterval); liveStatusInterval = null; }
    document.getElementById('liveFeed').src = '';
    document.getElementById('liveFeedContainer').style.display = 'none';
    document.getElementById('startCamBtn').disabled = false;
    document.getElementById('startCamBtn').style.background = 'var(--accent)';
    document.getElementById('startCamBtn').style.color = 'var(--btn-text)';
    document.getElementById('stopCamBtn').disabled = true;
    document.getElementById('stopCamBtn').style.background = 'var(--border-color)';
    document.getElementById('stopCamBtn').style.color = 'var(--text-muted)';
    fetch('/live/stop', {method: 'POST'}).catch(function(){});
  }

  function updateLiveStatus() {
    fetch('/live/status').then(r => r.json()).then(s => {
      document.getElementById('liveFps').textContent = 'FPS: ' + (s.fps || 0).toFixed(1);
      document.getElementById('liveFaceCount').textContent = s.faces ? s.faces.length : 0;
      document.getElementById('livePpeCount').textContent = s.ppe_found ? s.ppe_found.length : 0;

      const comp = document.getElementById('liveCompliance');
      if (s.compliant) {
        comp.textContent = 'OK';
        comp.style.color = 'var(--accent)';
      } else {
        comp.textContent = 'FAIL';
        comp.style.color = 'var(--danger)';
      }

      const ppeItems = ['Helmet','Gloves','Vest','Boots','Goggles'];
      const found = new Set(s.ppe_found || []);
      let ppeHtml = '';
      ppeItems.forEach(item => {
        const ok = found.has(item);
        ppeHtml += '<li class="ppe-row"><div class="left">' +
          '<span class="dot ' + (ok ? 'dot-on' : 'dot-off') + '"></span>' +
          '<span class="name ' + (ok ? 'found' : 'missing') + '">' + item + '</span></div>' +
          '<div class="right-side"><span class="badge ' + (ok ? 'badge-found">Found' : 'badge-missing">Missing') + '</span></div></li>';
      });
      document.getElementById('livePpeList').innerHTML = ppeHtml;

      const faces = s.faces || [];
      // Don't rebuild face list while email is being sent (button would be destroyed)
      if (window._emailSending) return;
      if (faces.length === 0) {
        document.getElementById('liveFaceList').innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;text-align:center;padding:12px;">No faces detected</p>';
      } else {
        let fHtml = '';
        const missingPpe = s.missing_ppe || [];
        const isCompliant = s.compliant;
        window._liveFaces = faces;
        window._liveMissingPpe = missingPpe;
        faces.forEach(function(f, idx) {
          fHtml += '<div class="face-row">' +
            '<div class="face-avatar">' + (f.name ? f.name[0] : '?') + '</div>' +
            '<div><div class="face-name">' + f.name + '</div>' +
            '<div class="face-conf">Confidence: ' + f.confidence + '</div></div>';
          if (f.status === 'Identified') {
            if (!isCompliant && missingPpe.length > 0) {
              fHtml += '<button class="btn-email" onclick="sendEmailForFace(' + idx + ', this)">Send Email</button>';
            } else {
              fHtml += '<span class="badge badge-found">Compliant</span>';
            }
          } else {
            fHtml += '<span class="register-msg">Please register face</span>';
          }
          fHtml += '</div>';
        });
        document.getElementById('liveFaceList').innerHTML = fHtml;
      }
    }).catch(() => {});
  }

  window.addEventListener('beforeunload', () => { fetch('/live/stop', {method:'POST'}); });

  // ── Image Modal / Lightbox ────────────────────────────
  function openModal(imgSrc, info) {
    document.getElementById('modalImage').src = imgSrc;
    document.getElementById('modalInfo').textContent = info || '';
    document.getElementById('imageModal').classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeModal(e, force) {
    if (force || e.target === document.getElementById('imageModal')) {
      document.getElementById('imageModal').classList.remove('show');
      document.body.style.overflow = '';
    }
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.getElementById('imageModal').classList.remove('show');
      document.body.style.overflow = '';
    }
  });

  // Attach click to all frame-card images and result images
  document.querySelectorAll('.frame-card img').forEach(img => {
    img.addEventListener('click', () => {
      const info = img.closest('.frame-card');
      const time = info ? info.querySelector('.frame-time') : null;
      openModal(img.src, time ? 'Frame at ' + time.textContent : '');
    });
  });
  document.querySelectorAll('.result-image').forEach(img => {
    img.addEventListener('click', () => openModal(img.src, 'Detection Result'));
  });

  // ── Worker Registration ─────────────────────────────────
  let regStream = null;
  let regCaptured = [];

  function regStartCamera() {
    // Stop live camera first so browser can access webcam
    if (!document.getElementById('stopCamBtn').disabled) { stopLive(); }
    navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } })
      .then(stream => {
        regStream = stream;
        const video = document.getElementById('regVideo');
        video.srcObject = stream;
        document.getElementById('regVideoWrap').style.display = 'block';
        document.getElementById('regCamPlaceholder').style.display = 'none';
        document.getElementById('regStartCamBtn').disabled = true;
        document.getElementById('regStartCamBtn').style.background = 'var(--border-color)';
        document.getElementById('regStartCamBtn').style.color = 'var(--text-muted)';
        document.getElementById('regCaptureBtn').disabled = false;
        document.getElementById('regCaptureBtn').style.background = 'var(--accent)';
        document.getElementById('regCaptureBtn').style.color = 'var(--btn-text)';
      })
      .catch(err => alert('Cannot access camera: ' + err.message));
  }

  function regCaptureFrame() {
    const video = document.getElementById('regVideo');
    const canvas = document.getElementById('regCanvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
    regCaptured.push(dataUrl);

    const grid = document.getElementById('regCapturedGrid');
    const img = document.createElement('img');
    img.src = dataUrl;
    img.title = 'Photo ' + regCaptured.length;
    grid.appendChild(img);

    const count = regCaptured.length;
    document.getElementById('regCapturedCount').textContent = count + ' photo(s) captured' + (count < 3 ? ' (minimum 3)' : ' — ready!');
    if (count >= 3) {
      document.getElementById('regSubmitBtn').disabled = false;
    }
  }

  function regStopCamera() {
    if (regStream) {
      regStream.getTracks().forEach(t => t.stop());
      regStream = null;
    }
    document.getElementById('regVideoWrap').style.display = 'none';
    document.getElementById('regCamPlaceholder').style.display = 'block';
    document.getElementById('regStartCamBtn').disabled = false;
    document.getElementById('regStartCamBtn').style.background = 'var(--accent)';
    document.getElementById('regStartCamBtn').style.color = 'var(--btn-text)';
    document.getElementById('regCaptureBtn').disabled = true;
    document.getElementById('regCaptureBtn').style.background = 'var(--border-color)';
    document.getElementById('regCaptureBtn').style.color = 'var(--text-muted)';
  }

  function regSubmit() {
    const name = document.getElementById('regName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    if (!name || !email) { alert('Please enter name and email'); return; }
    if (regCaptured.length < 3) { alert('Capture at least 3 photos'); return; }

    const btn = document.getElementById('regSubmitBtn');
    btn.classList.add('loading');
    btn.textContent = 'Registering...';
    btn.disabled = true;

    const statusEl = document.getElementById('regStatus');
    statusEl.className = 'reg-status';
    statusEl.style.display = 'none';

    fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name, email: email, images: regCaptured })
    })
    .then(r => r.json())
    .then(data => {
      btn.classList.remove('loading');
      if (data.status === 'ok') {
        statusEl.className = 'reg-status show success';
        statusEl.textContent = data.message;
        // Reset form
        regStopCamera();
        document.getElementById('regName').value = '';
        document.getElementById('regEmail').value = '';
        regCaptured = [];
        document.getElementById('regCapturedGrid').innerHTML = '';
        document.getElementById('regCapturedCount').textContent = '0 photos captured (minimum 3)';
        btn.textContent = 'Register Worker';
        btn.disabled = true;
        loadRegisteredWorkers();
      } else {
        statusEl.className = 'reg-status show error';
        statusEl.textContent = data.message || 'Registration failed';
        btn.textContent = 'Register Worker';
        btn.disabled = false;
      }
    })
    .catch(err => {
      btn.classList.remove('loading');
      btn.textContent = 'Register Worker';
      btn.disabled = false;
      statusEl.className = 'reg-status show error';
      statusEl.textContent = 'Error: ' + err.message;
    });
  }

  function loadRegisteredWorkers() {
    fetch('/registered-workers').then(r => r.json()).then(data => {
      const list = document.getElementById('workersList');
      const workers = data.workers || [];
      if (workers.length === 0) {
        list.innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;text-align:center;padding:12px;">No workers registered yet</p>';
        return;
      }
      let html = '';
      workers.forEach(w => {
        html += '<div class="worker-list-item">' +
          '<div class="face-avatar">' + (w.name ? w.name[0].toUpperCase() : '?') + '</div>' +
          '<div><div class="face-name">' + w.name + '</div>' +
          '<div class="face-conf">' + w.id + ' &middot; ' + w.email + '</div></div>' +
          '<button class="btn-delete" onclick="deleteWorker(\'' + w.id + '\', this)">Delete</button></div>';
      });
      list.innerHTML = html;
    }).catch(() => {
      document.getElementById('workersList').innerHTML = '<p style="color:var(--text-muted);font-size:0.82rem;text-align:center;padding:12px;">Could not load workers</p>';
    });
  }

  // Load registered workers when switching to register tab
  const origSwitchTab = switchTab;
  switchTab = function(tab, navEl) {
    origSwitchTab(tab, navEl);
    if (tab === 'register') loadRegisteredWorkers();
  };

  // Global flag to pause face list refresh while sending email
  window._emailSending = false;

  function showEmailToast(msg, isSuccess) {
    var el = document.getElementById('emailStatus');
    if (!el) return;
    el.className = 'email-toast show ' + (isSuccess ? 'toast-success' : 'toast-error');
    el.innerHTML = (isSuccess ? '&#10003; ' : '&#10007; ') + msg;
    setTimeout(function() { el.className = 'email-toast'; }, 6000);
  }

  function sendEmailForFace(idx, btnEl) {
    var f = window._liveFaces[idx];
    if (!f) return;
    window._emailSending = true;
    if (btnEl) { btnEl.disabled = true; btnEl.textContent = 'Sending...'; }

    fetch('/send-violation-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        worker_id: f.worker_id || '',
        worker_name: f.name || '',
        worker_email: f.email || '',
        missing_ppe: window._liveMissingPpe || []
      })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      window._emailSending = false;
      if (data.status === 'ok') {
        showEmailToast('Email sent successfully to ' + (f.email || ''), true);
      } else {
        showEmailToast(data.message || 'Failed to send email', false);
      }
    })
    .catch(function(err) {
      window._emailSending = false;
      showEmailToast('Error: ' + err.message, false);
    });
  }

  function deleteWorker(workerId, btnEl) {
    if (!confirm('Delete worker ' + workerId + '? This cannot be undone.')) return;
    if (btnEl) { btnEl.disabled = true; btnEl.textContent = 'Deleting...'; }
    fetch('/delete-worker', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ worker_id: workerId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        loadRegisteredWorkers();
      } else {
        alert(data.message || 'Failed to delete worker');
        if (btnEl) { btnEl.disabled = false; btnEl.textContent = 'Delete'; }
      }
    })
    .catch(err => {
      alert('Error: ' + err.message);
      if (btnEl) { btnEl.disabled = false; btnEl.textContent = 'Delete'; }
    });
  }
