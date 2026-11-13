/* core.js — phần dùng chung cho index.html, ta.html, gv.html (Agent C).
   Chỉ gọi API theo CONTRACT.md. Không CDN, không gọi OpenAI từ trình duyệt.
   ?mock=K1|K2|K3|K6  → phát lại /api/replay/<K>, trạng thái giả lập lưu ở localStorage để TA/GV cùng thấy.
   ?annotate=1        → bật sẵn lớp "Chú thích". */
(function () {
  'use strict';

  const params = new URLSearchParams(location.search);
  const MOCK = params.get('mock');
  const REPLAYS = ['K1', 'K2', 'K3', 'K6'];
  const DEFAULT_NOW = '2026-11-13T22:40:00+07:00';

  /* ---------- DOM ---------- */
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (v == null || v === false) continue;
        if (k === 'class') el.className = v;
        else if (k === 'html') el.innerHTML = v;
        else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? '' : v);
      }
    }
    for (const kid of kids.flat(Infinity)) {
      if (kid == null || kid === false) continue;
      el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    }
    return el;
  }

  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  /* ---------- Biểu tượng (SVG nhúng, không tải ngoài) ---------- */
  const ICONS = {
    check: '<path d="M20 6 9 17l-5-5"/>',
    alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    nosrc: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3M8.5 8.5l5 5M13.5 8.5l-5 5"/>',
    lock: '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    shield: '<path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6l-8-3z"/><path d="m9 12 2 2 4-4"/>',
    flag: '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    send: '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z"/>',
    bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3z"/>',
    trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    refresh: '<path d="M3 12a9 9 0 0 1 15.5-6.3L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.3L3 16M3 21v-5h5"/>',
    play: '<path d="M6 4l14 8-14 8V4z"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    inbox: '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.7 4H7.3a2 2 0 0 0-1.8 1.1z"/>',
    msg: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    tag: '<path d="M4 4h7l9 9-7 7-9-9V4z"/><circle cx="8" cy="8" r="1.2"/>',
    chart: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    hide: '<path d="M3 3l18 18M10.6 5.1A10 10 0 0 1 22 12a13 13 0 0 1-2.6 3.4M6.5 6.6A13 13 0 0 0 2 12c1.8 4 5.5 7 10 7 1.6 0 3-.3 4.4-1M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
    book: '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5z"/><path d="M4 19a2 2 0 0 1 2-2h13"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    users: '<circle cx="9" cy="8" r="3.5"/><path d="M2 21a7 7 0 0 1 14 0M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.5a7 7 0 0 1 4 6.5"/>',
    cap: '<path d="M2 9l10-5 10 5-10 5L2 9z"/><path d="M6 11.5V16c1.5 1.6 3.6 2.5 6 2.5s4.5-.9 6-2.5v-4.5M22 9v6"/>',
    bot: '<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9.5 16h5"/>',
  };
  function icon(name) {
    const t = document.createElement('template');
    t.innerHTML = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (ICONS[name] || '') + '</svg>';
    return t.content.firstChild;
  }

  /* ---------- Thời gian: hiển thị theo giờ ghi trong chuỗi ISO, không phụ thuộc múi giờ của máy ---------- */
  function parts(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(iso || '');
    if (!m) return null;
    return { d: +m[3], mo: +m[2], hh: m[4], mm: m[5], min: +m[4] * 60 + +m[5], day: Date.UTC(+m[1], +m[2] - 1, +m[3]) / 864e5 };
  }
  function fmtWhen(iso, nowIso) {
    const p = parts(iso);
    if (!p) return iso || '';
    const n = parts(nowIso);
    const hm = p.hh + ':' + p.mm;
    const dm = p.d + '/' + p.mo;
    if (n) {
      const diff = p.day - n.day;
      if (diff === 0) return hm + ' hôm nay';
      if (diff === 1) return hm + (+p.hh < 12 ? ' sáng mai' : ' ngày mai') + ' (' + dm + ')';
    }
    return hm + ' ngày ' + dm;
  }
  function minutesBetween(aIso, bIso) {
    const a = Date.parse(aIso), b = Date.parse(bIso);
    return isNaN(a) || isNaN(b) ? null : Math.round((b - a) / 6e4);
  }
  function fmtDuration(min) {
    const hh = Math.floor(min / 60), mm = min % 60;
    return (hh ? hh + ' giờ ' : '') + mm + ' phút';
  }

  /* ---------- API thật ---------- */
  const enc = encodeURIComponent;
  const Live = {
    async req(method, path, body) {
      const res = await fetch(path, {
        method,
        headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      let data = null;
      try { data = await res.json(); } catch (e) { /* thân rỗng */ }
      if (!res.ok) {
        const err = new Error('HTTP ' + res.status);
        err.status = res.status;
        err.data = data;
        throw err;
      }
      return data;
    },
    session(now) { return this.req('POST', '/api/session', now ? { now } : {}); },
    course(sid) { return this.req('GET', '/api/course?session_id=' + enc(sid)); },
    chat(sid, message) { return this.req('POST', '/api/chat', { session_id: sid, message }); },
    state() { return this.req('GET', '/api/state'); },
    confirm(id, sid) { return this.req('POST', '/api/actions/' + enc(id) + '/confirm', { session_id: sid }); },
    cancel(id, sid) { return this.req('POST', '/api/actions/' + enc(id) + '/cancel', { session_id: sid }); },
    faqDelete(id) { return this.req('DELETE', '/api/faq/' + enc(id)); },
    faqApprove(id) { return this.req('POST', '/api/faq/' + enc(id) + '/approve'); },
    faqReject(id) { return this.req('POST', '/api/faq/' + enc(id) + '/reject'); },
    ticketClose(id) { return this.req('POST', '/api/tickets/' + enc(id) + '/close'); },
    feedback(sid, mid, text) { return this.req('POST', '/api/feedback', { session_id: sid, message_id: mid, text }); },
    replay(name) { return this.req('GET', '/api/replay/' + enc(name)); },
    reset() { return this.req('POST', '/api/reset'); },
  };

  /* ---------- API phát lại: cùng giao diện hàm với Live, trạng thái ở localStorage ---------- */
  const MKEY = 't2proto.mock.v1';
  let memStore = null;
  const emptyStore = () => ({ pending_actions: [], ta_queue: [], faq: [], tickets: [], flagged_sections: [], stats: { bt3_hint_sessions: 0 }, _hint: 0 });
  function mload() {
    try {
      const raw = localStorage.getItem(MKEY);
      if (raw) return JSON.parse(raw);
    } catch (e) { /* cửa sổ riêng tư: dùng bộ nhớ */ }
    return memStore || emptyStore();
  }
  function msave(s) {
    memStore = s;
    try { localStorage.setItem(MKEY, JSON.stringify(s)); } catch (e) { /* bỏ qua */ }
  }
  function notFound() { const e = new Error('HTTP 404'); e.status = 404; return e; }

  const Mock = {
    _replay: null, _i: 0, _now: DEFAULT_NOW,
    async loadReplay() {
      if (!this._replay) this._replay = await Live.replay(REPLAYS.includes(MOCK) ? MOCK : 'K1');
      return this._replay;
    },
    async session(now) {
      let rp = null;
      try { rp = await this.loadReplay(); } catch (e) { /* báo lỗi ở bước course */ }
      this._now = now || (rp && rp.meta && rp.meta.now) || DEFAULT_NOW;
      this._i = 0;
      const st = mload(); st._hint = 0; msave(st);
      return { session_id: 'mock', now: this._now };
    },
    async course() {
      const s = await Live.session(this._now);
      const c = await Live.course(s.session_id);
      c.flagged_sections = mload().flagged_sections;
      return c;
    },
    async chat() {
      const rp = await this.loadReplay();
      await sleep(700);
      const turn = rp.turns[this._i++];
      if (!turn) {
        return { message_id: 'mock-end-' + this._i, reply: 'Bản phát lại đã hết lượt đã lưu. Bấm "Chat với AI thật" ở trên để hỏi tiếp.', confidence: 'no_source', citations: [], notes: [{ type: 'info', text: 'Chế độ phát lại không gọi AI.' }], events: [], pending_actions: [], hint_progress: null, trace: [] };
      }
      const r = turn.response;
      const st = mload();
      for (const a of r.pending_actions || []) {
        if (!st.pending_actions.some((x) => x.id === a.id) && !st.ta_queue.some((x) => x.id === a.id)) st.pending_actions.push(Object.assign({ question: a.summary }, a));
      }
      for (const ev of r.events || []) {
        if (ev.type !== 'flag_created') continue;
        const d = ev.data || {};
        const tr = (r.trace || []).find((x) => x.tool === 'bao_loi_tai_lieu');
        const args = (tr && tr.args) || {};
        const id = d.ticket_id || 'DOC-1';
        const sec = d.section || args.section;
        const tk = st.tickets.find((x) => x.id === id);
        if (tk) tk.status = 'open';
        else st.tickets.push({ id, type: 'doc_flag', section: sec, claim: args.claim || '', counterexample: args.counterexample || '', status: 'open', created_at: this._now });
        if (sec && !st.flagged_sections.includes(sec)) st.flagged_sections.push(sec);
      }
      if (r.hint_progress) {
        st._hint = r.hint_progress.level;
        st.stats.bt3_hint_sessions = Math.max(1, st.stats.bt3_hint_sessions);
      }
      msave(st);
      return r;
    },
    async state() {
      const st = mload();
      const out = Object.assign({}, st);
      delete out._hint;
      return out;
    },
    async confirm(id) {
      const st = mload();
      const i = st.pending_actions.findIndex((x) => x.id === id);
      if (i < 0) throw notFound();
      const a = st.pending_actions.splice(i, 1)[0];
      const item = {
        id: a.id, question: a.question || a.summary, ta_reply_time: a.ta_reply_time, after_deadline: a.after_deadline,
        ai_summary: st._hint ? 'AI đã gợi ý tới nấc ' + st._hint + '/3, chưa đưa đáp số' : 'AI chưa gợi ý bài, chưa đưa đáp số',
      };
      st.ta_queue.push(item);
      msave(st);
      return { ok: true, ta_queue_item: item };
    },
    async cancel(id) {
      const st = mload();
      st.pending_actions = st.pending_actions.filter((x) => x.id !== id);
      msave(st);
      return { ok: true };
    },
    async faqDelete(id) { const st = mload(); st.faq = st.faq.filter((f) => f.id !== id); msave(st); return { ok: true }; },
    async _faqSet(id, status) {
      const st = mload();
      const f = st.faq.find((x) => x.id === id);
      if (!f) throw notFound();
      f.status = status; msave(st);
      return { ok: true, status };
    },
    faqApprove(id) { return this._faqSet(id, 'published'); },
    faqReject(id) { return this._faqSet(id, 'rejected'); },
    async ticketClose(id) {
      const st = mload();
      const tk = st.tickets.find((x) => x.id === id);
      if (!tk) throw notFound();
      tk.status = 'closed';
      const stillOpen = st.tickets.some((x) => x.status === 'open' && x.type === 'doc_flag' && x.section === tk.section);
      if (!stillOpen) st.flagged_sections = st.flagged_sections.filter((s) => s !== tk.section);
      msave(st);
      return { ok: true };
    },
    async feedback(_sid, mid, text) {
      const st = mload();
      const id = 'DOC-' + (st.tickets.length + 1);
      st.tickets.push({ id, type: 'feedback', message_id: mid, text, status: 'open', created_at: this._now });
      msave(st);
      return { ok: true, ticket_id: id };
    },
    replay(name) { return Live.replay(name); },
    async reset() { msave(emptyStore()); return { ok: true }; },
  };

  const Api = MOCK ? Mock : Live;

  /* ---------- Thông báo nhỏ ---------- */
  let toastTimer = null;
  function toast(text) {
    $$('.toast').forEach((t) => t.remove());
    const el = h('div', { class: 'toast', role: 'status' }, text);
    document.body.append(el);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.remove(), 3200);
  }

  /* ---------- Chú thích: huy hiệu số trên phần tử có data-hax (ảnh đánh số cho spec §5) ---------- */
  const HAX = [
    [1, 'Thẻ 📌 Bài 3 + dòng giới thiệu trợ lý', 'G1, G2', '—'],
    [2, 'Chip mã mục + mục tô sáng bên trái', 'PAIR Explainability', 'tự làm (tra_cuu_tai_lieu)'],
    [3, 'Thẻ độ chắc do server tính', 'G2, PAIR Calibrated Trust', '—'],
    [4, 'Câu trả lời kèm giới hạn / hỏi lại', 'G10', '—'],
    [5, 'Banner cảnh báo + phản ví dụ, nêu lý do', 'G11', 'tự làm (bao_loi_tai_lieu)'],
    [6, 'Nút "Báo sai"', 'G15', '—'],
    [7, 'Nháp FAQ + nút "Xoá nháp" (hoàn tác)', 'G8, G9', 'tự làm (soan_FAQ)'],
    [8, 'Hộp "Việc đang chờ bạn": Xác nhận gửi TA', 'G9 (kiểm soát)', 'cần duyệt (chuyen_TA)'],
    [9, 'Khung 🔒 không khả dụng + Gợi ý n/3 không có nấc đáp số', 'G10, PAIR Graceful Failure', 'cấm (không có tool, không có nút)'],
    [10, 'Trang TA / Giảng viên: ai được báo', 'PAIR Errors + Graceful Failure', 'cần duyệt (dang_FAQ)'],
  ];
  let legendEl = null;
  const annot = {
    on: false,
    init() {
      let saved = null;
      try { saved = localStorage.getItem('t2proto.annot'); } catch (e) { /* bỏ qua */ }
      const q = params.get('annotate');
      this.set(q != null ? q === '1' : saved === '1', true);
    },
    set(v, silent) {
      this.on = !!v;
      document.body.classList.toggle('annotate', this.on);
      if (!silent) { try { localStorage.setItem('t2proto.annot', this.on ? '1' : '0'); } catch (e) { /* bỏ qua */ } }
      const box = $('#annot-toggle');
      if (box) box.checked = this.on;
      this.refresh();
    },
    refresh() {
      $$('[data-hax-on]').forEach((e) => e.removeAttribute('data-hax-on'));
      if (legendEl) legendEl.hidden = !this.on;
      if (!this.on) return;
      const inChat = {};
      const shown = new Set();
      $$('[data-hax]').forEach((e) => {
        if (e.offsetParent === null) return;
        if (e.closest('#messages')) inChat[e.dataset.hax] = e; // trong khung chat: chỉ đánh số tin mới nhất
        else { e.setAttribute('data-hax-on', ''); shown.add(e.dataset.hax); }
      });
      for (const [n, e] of Object.entries(inChat)) { e.setAttribute('data-hax-on', ''); shown.add(n); }
      if (legendEl) $$('li', legendEl).forEach((li) => li.classList.toggle('absent', !shown.has(li.dataset.n)));
    },
  };
  function mountLegend() {
    legendEl = h('details', { class: 'legend', open: true, hidden: true },
      h('summary', null, icon('tag'), 'Chú thích 1–10', h('span', null, 'nguyên tắc · mức tự chủ')),
      h('ol', null, HAX.map(([n, what, rule, auto]) => h('li', { 'data-n': String(n) },
        h('span', { class: 'n' }, n),
        h('span', null, h('span', { class: 'what' }, what), h('br'), h('span', { class: 'why' }, h('b', null, rule), auto === '—' ? '' : ' · ' + auto))))));
    const side = $('.col-side');
    if (side) { legendEl.classList.add('is-docked'); side.append(legendEl); }
    else document.body.append(legendEl);
  }

  /* ---------- Giao diện sáng / tối ---------- */
  function applyTheme(t) {
    if (t === 'light') document.documentElement.dataset.theme = 'light';
    else delete document.documentElement.dataset.theme;
  }
  try { applyTheme(localStorage.getItem('t2proto.theme')); } catch (e) { /* bỏ qua */ }

  /* ---------- Thanh trên ---------- */
  function mountTopbar(page, opts) {
    opts = opts || {};
    const bar = $('#topbar');
    const q = MOCK ? '?mock=' + enc(MOCK) : '';
    const tab = (id, href, label, ic) => h('a', { class: 'role' + (page === id ? ' is-active' : ''), href: href + q, 'aria-current': page === id ? 'page' : null }, icon(ic), label);

    const themeBtn = h('button', {
      class: 'btn btn-ghost btn-icon', type: 'button', title: 'Đổi giao diện sáng / tối', 'aria-label': 'Đổi giao diện sáng / tối',
      onclick() {
        const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
        applyTheme(next);
        try { localStorage.setItem('t2proto.theme', next); } catch (e) { /* bỏ qua */ }
        themeBtn.replaceChildren(icon(next === 'light' ? 'moon' : 'sun'));
      },
    }, icon(document.documentElement.dataset.theme === 'light' ? 'moon' : 'sun'));

    const demo = h('div', { class: 'demo-group', title: 'Công cụ demo, không thuộc sản phẩm' }, h('span', { class: 'demo-tag' }, 'DEMO'));
    if (page === 'student') {
      const clock = h('input', { type: 'datetime-local', id: 'clock', 'aria-label': 'Giờ demo', onchange() { if (clock.value && opts.onClock) opts.onClock(clock.value + ':00+07:00'); } });
      demo.append(h('label', { class: 'demo-ctl' }, 'Giờ', clock));
      demo.append(h('details', { class: 'menu', id: 'replay-menu' },
        h('summary', { class: 'btn btn-sm' }, icon('play'), 'Phát lại bản đã lưu'),
        h('div', { class: 'menu-pop' },
          [['K1', 'Tài liệu có câu sai (§3.3)'], ['K2', 'Gọi TA lúc 22:40'], ['K3', 'Câu hỏi mơ hồ'], ['K6', 'Nhượng dần qua 3 lượt']]
            .map(([k, label]) => h('a', { href: 'index.html?mock=' + k }, h('b', null, k), label)),
          MOCK ? [h('hr'), h('a', { href: 'index.html' }, h('b', null, '←'), 'Chat với AI thật')] : null)));
    }
    demo.append(h('button', {
      class: 'btn btn-ghost btn-sm', type: 'button', title: 'Xoá mọi trạng thái để demo lại',
      async onclick() {
        try { await Api.reset(); } catch (e) { /* vẫn tải lại */ }
        location.reload();
      },
    }, icon('refresh'), 'Đặt lại'));

    bar.replaceChildren(
      h('div', { class: 'brand' },
        h('span', { class: 'brand-mark' }, icon('bulb')),
        h('div', null, h('div', { class: 'brand-name' }, 'Trợ lý học bài'), h('div', { class: 'brand-sub', id: 'brand-sub' }, 'Nhập môn phân tích dữ liệu'))),
      h('nav', { class: 'roles', 'aria-label': 'Chuyển vai', 'data-hax': page === 'student' ? '10' : null },
        tab('student', 'index.html', 'Học viên', 'user'), tab('ta', 'ta.html', 'TA', 'users'), tab('gv', 'gv.html', 'Giảng viên', 'cap')),
      h('div', { class: 'tools' },
        h('span', { class: 'mode' + (MOCK ? ' is-mock' : ''), id: 'mode' }, MOCK ? 'Phát lại' + (REPLAYS.includes(MOCK) ? ' · ' + MOCK : '') : 'Trực tiếp'),
        demo,
        h('label', { class: 'switch', title: 'Phủ số 1–10 lên các phần tử thiết kế (ảnh cho spec §5)' },
          h('input', { type: 'checkbox', id: 'annot-toggle', onchange(e) { annot.set(e.target.checked); } }), h('i'), 'Chú thích'),
        themeBtn));

    document.addEventListener('click', (e) => {
      const menu = $('#replay-menu');
      if (menu && menu.open && !menu.contains(e.target)) menu.open = false;
    });
    mountLegend();
    annot.init();
  }

  function setConn(ok) {
    const m = $('#mode');
    if (!m) return;
    m.classList.toggle('is-off', !ok);
    m.textContent = ok ? (MOCK ? 'Phát lại' + (REPLAYS.includes(MOCK) ? ' · ' + MOCK : '') : 'Trực tiếp') : 'Mất kết nối máy chủ';
  }

  window.App = { $, $$, h, esc, sleep, icon, Api, Live, MOCK, REPLAYS, DEFAULT_NOW, parts, fmtWhen, minutesBetween, fmtDuration, toast, annot, mountTopbar, setConn };
})();
