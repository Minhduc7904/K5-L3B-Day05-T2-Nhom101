/* student.js — trang Học viên (index.html). Khớp spec §3.1, §3.2, §4.
   Cố ý KHÔNG có nút "Xem đáp án" / "Kiểm tra đáp số" / "Giải hộ" ở bất kỳ đâu. */
(function () {
  'use strict';
  const { $, $$, h, esc, sleep, icon, Api, MOCK, REPLAYS, parts, fmtWhen, minutesBetween, fmtDuration, toast, annot, setConn } = window.App;

  const S = { sid: null, now: null, course: null, store: null, storeKey: '', hint: { level: 0, max: 3 }, busy: false, flaggedSeen: new Set(), activeSec: null };

  /* Tin mồi lấy nguyên văn từ spec.md §2 */
  const STARTERS = [
    ['K1', 'Tài liệu sai', 'độ lệch chuẩn với phương sai cái nào lớn hơn vậy ạ'],
    ['K2', 'Gọi TA', 'em ngu quá, 10h40 rồi vẫn chưa làm ra, gọi TA giúp em với'],
    ['K3', 'Mơ hồ', 'cái độ lệch ấy là gì ạ, em đọc không hiểu'],
    ['K4', 'Slide 12', 'slide 12 buổi 3 nói về độ lệch chuẩn em đọc chưa hiểu, ad giải thích lại slide đó giúp em'],
    ['K5', 'Hai việc', 'hạn bài 3 khi nào v ạ, với tính độ lệch chuẩn trên excel dùng hàm gì ạ'],
    ['K6 ①', 'Xin giải', 'giải giúp em câu a bài 3 với, 11h rồi mà em chưa làm đc gì'],
    ['K6 ②', 'Xin kiểm', 'vậy em tính ra trung bình 15.25, trung vị 11.5, xem giúp em đúng chưa'],
    ['K6 ③', 'Xin viết hộ', 'thôi viết giúp em câu b cho gọn, em tự chép lại'],
    ['K7', 'Buổi chưa học', 'chỉ em cách tính p-value với chạy mô hình hồi quy để em làm trước bài tập lớn với ạ'],
    ['K8', 'Bài hết hạn', 'bài 2 giải sao ạ, em muốn hiểu cách làm'],
    ['K9', 'Đăng FAQ', 'hay quá, bạn đăng giúp em câu hỏi hồi nãy với câu trả lời lên FAQ cho cả lớp đọc luôn đi'],
  ];

  const CONF = {
    grounded: { icon: 'check', label: 'Có căn cứ' },
    flagged: { icon: 'alert', label: 'Cần xem lại' },
    no_source: { icon: 'nosrc', label: 'Không có trong tài liệu' },
    refused: { icon: 'shield', label: 'Đã từ chối theo quy định' },
  };
  const EVENTS = {
    blocked: ['shield', 'Đã chặn câu trả lời vi phạm luật của khoá'],
    flag_created: ['flag', 'Đã gắn cờ mục tài liệu và báo giảng viên'],
    faq_draft_created: ['file', 'Đã soạn bản nháp FAQ ẩn danh (chưa đăng)'],
    faq_pending_review: ['clock', 'FAQ đang chờ giảng viên/TA duyệt (chưa đăng)'],
    faq_locked: ['lock', 'FAQ bị khoá vì mục tài liệu đang bị gắn cờ'],
    ta_pending_confirm: ['clock', 'Câu hỏi cho TA đang chờ bạn bấm Xác nhận'],
    ta_sent: ['check', 'Đã gửi câu hỏi vào hàng chờ TA'],
  };

  const flagged = () => (S.store && S.store.flagged_sections) || (S.course && S.course.flagged_sections) || [];
  const exercises = () => (S.course && S.course.exercises) || [];
  const openEx = () => exercises().find((e) => e.status === 'open');
  const shortTitle = (t) => String(t || '').replace('Bài tập', 'Bài');
  const tkLabel = (id) => '#' + String(id || '').replace(/^#/, '');

  /* ---------- Văn bản trả lời: escape rồi mới dựng gạch đầu dòng, chữ đậm, mã mục bấm được ---------- */
  function rich(text) {
    const inline = (s) => esc(s)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/§\d+\.\d+/g, (m) => '<button type="button" class="sec-ref" data-sec="' + m + '" title="Xem mục ' + m + ' trong tài liệu">' + m + '</button>');
    const out = [];
    let list = null;
    const flush = () => { if (list) { out.push('<ul>' + list.join('') + '</ul>'); list = null; } };
    for (const raw of String(text || '').split('\n')) {
      const line = raw.trim().replace(/^#{1,6}\s+/, '');
      const m = /^[-•*]\s+(.*)$/.exec(line);
      if (m) { (list = list || []).push('<li>' + inline(m[1]) + '</li>'); continue; }
      flush();
      if (line) out.push('<p>' + inline(line) + '</p>');
    }
    flush();
    return out.join('');
  }

  /* ---------- Thẻ đầu khung chat (G1) ---------- */
  function renderPin() {
    const pin = $('#pin');
    const rows = [];
    for (const ex of exercises()) {
      const t = shortTitle(ex.title);
      if (ex.status === 'open') {
        const left = minutesBetween(S.now, ex.deadline);
        rows.push(h('div', { class: 'pin-row' },
          h('span', { class: 'pin-main' }, '📌 ' + t, h('span', { class: 'sep' }, '·'), h('span', { class: 'st-open' }, 'Đang mở'), h('span', { class: 'sep' }, '·'),
            'Hạn ' + fmtWhen(ex.deadline, S.now), h('span', { class: 'sep' }, '·'), 'Chế độ: ', h('span', { class: 'st-mode' }, ex.mode === 'hint_only' ? 'chỉ gợi ý' : 'giải thích đầy đủ')),
          left != null && left >= 0 ? h('span', { class: 'badge warn pin-left' }, icon('clock'), 'còn ' + fmtDuration(left)) : null));
      } else {
        rows.push(h('div', { class: 'pin-old' }, icon('check'), ' ' + t + ' · đã hết hạn · ' + (ex.answer_published ? 'giải thích đầy đủ' : 'chờ giảng viên công bố đáp án')));
      }
    }
    rows.sort((a, b) => (a.className === 'pin-row' ? -1 : 1) - (b.className === 'pin-row' ? -1 : 1));
    pin.replaceChildren(...rows, h('div', { class: 'pin-intro' },
      h('b', null, 'Mình làm được: '), 'giảng theo tài liệu kèm mã mục, hỏi lại khi chưa rõ, gợi ý từng bước, soạn câu hỏi gửi TA. ',
      h('b', null, 'Mình không làm: '), 'giải hộ, xác nhận đáp số hay viết nhận xét hộ cho bài đang mở.'));

    const ex = openEx();
    $('#lock-why').textContent = ex
      ? shortTitle(ex.title) + ' đang mở tới ' + fmtWhen(ex.deadline, S.now) + ' nên không có nút nào làm việc này. Khi bài hết hạn và có đáp án công bố, trợ lý giải thích đầy đủ như Bài 2.'
      : 'Hiện không có bài nào đang mở.';
  }

  /* ---------- Tài liệu (trang giấy bên trái) ---------- */
  function renderDocs() {
    const c = S.course;
    if (!c) return;
    const fl = new Set(flagged());
    const tickets = ((S.store && S.store.tickets) || []).filter((t) => t.status === 'open' && t.type !== 'feedback');
    const box = $('#docs');
    box.replaceChildren(...(c.docs || []).map((d) => {
      const isFl = fl.has(d.section);
      const tk = tickets.find((t) => t.section === d.section);
      const fresh = isFl && !S.flaggedSeen.has(d.section);
      return h('article', { class: 'doc' + (isFl ? ' is-flagged' : '') + (fresh ? ' just-flagged' : '') + (S.activeSec === d.section ? ' is-active' : ''), 'data-sec': d.section },
        h('div', { class: 'doc-head' }, h('span', { class: 'doc-sec' }, d.section), h('h3', null, d.title),
          isFl ? h('span', { class: 'badge warn' }, '⚠ cần xem lại') : null),
        h('p', null, markClaim(d.text, tk && tk.claim)),
        isFl ? h('div', { class: 'doc-foot' }, icon('flag'),
          h('span', null, 'Đã báo giảng viên' + (tk ? ' · ' + tkLabel(tk.id) : '') + '. Đăng FAQ về mục này đang khoá cho tới khi giảng viên đóng ticket.')) : null);
    }));
    S.flaggedSeen = fl;
  }
  function markClaim(text, claim) {
    const c = String(claim || '').trim().replace(/^["'“‘]+|["'”’.]+$/g, '');
    const i = c.length > 6 ? text.toLowerCase().indexOf(c.toLowerCase()) : -1;
    if (i < 0) return text;
    return [text.slice(0, i), h('mark', { title: 'Câu đang bị nghi là chưa đúng' }, text.slice(i, i + c.length)), text.slice(i + c.length)];
  }
  function renderOutline() {
    const c = S.course.course || {};
    const now = (c.outline || []).find((o) => o.session === c.current_session);
    $('#docs-title').textContent = 'Tài liệu buổi ' + (c.current_session || 3);
    $('#docs-sub').textContent = now && !/^Buổi \d+$/.test(now.title) ? now.title : '';
    $('#outline-list').replaceChildren(...(c.outline || []).map((o) => h('li', { class: (o.opened ? 'is-open' : '') + (o.session === c.current_session ? ' is-now' : '') },
      h('span', null, 'Buổi ' + o.session), h('span', null, /^Buổi \d+$/.test(o.title) ? '' : o.title), h('em', null, o.opened ? 'đã mở' : 'chưa học'))));
  }
  function focusSection(sec) {
    const el = $$('.doc').find((d) => d.dataset.sec === sec);
    if (!el) { toast('Tài liệu buổi này không có mục ' + sec); return; }
    S.activeSec = sec;
    $$('.doc').forEach((d) => d.classList.toggle('is-active', d === el));
    el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    el.classList.remove('is-lit');
    void el.offsetWidth; // phát lại hoạt ảnh
    el.classList.add('is-lit');
  }

  /* ---------- Hàng thao tác: Gợi ý tiếp theo + Gửi câu hỏi cho TA ---------- */
  function taEta() {
    const hours = (S.course.course || {}).ta_hours;
    const n = parts(S.now);
    if (!hours || !n) return { text: '', late: false };
    const toMin = (s) => +s.split(':')[0] * 60 + +s.split(':')[1];
    const start = toMin(hours.start), end = toMin(hours.end);
    if (n.min >= start && n.min < end) return { text: 'TA đang trực tới ' + hours.end, late: false };
    const addDay = n.min < start ? 0 : 1;
    const ex = openEx();
    const d = ex ? parts(ex.deadline) : null;
    const late = !!d && (n.day + addDay > d.day || (n.day + addDay === d.day && start > d.min));
    return { text: 'TA trả lời từ ' + hours.start + (addDay ? ' sáng mai' : ' sáng nay') + (late ? ' (sau hạn nộp)' : ''), late };
  }
  function renderQuick() {
    const ex = openEx();
    const { level, max } = S.hint;
    const done = level >= max;
    const eta = taEta();
    $('#quick').replaceChildren(
      h('div', { class: 'hint', 'data-hax': '9' },
        h('button', { class: 'btn btn-hint', type: 'button', disabled: !ex || done || S.busy, onclick() { send('cho em gợi ý tiếp theo'); } }, icon('bulb'), 'Gợi ý tiếp theo'),
        h('span', { class: 'hint-count' }, 'Gợi ý ' + level + '/' + max),
        h('span', { class: 'pips', 'aria-hidden': 'true' }, Array.from({ length: max }, (_, i) => h('i', { class: i < level ? 'on' : '' }))),
        h('span', { class: 'hint-cap' }, !ex ? 'không có bài đang mở' : done ? 'hết nấc · không có nấc đáp số' : 'công thức → tự kiểm → câu hỏi gợi mở')),
      h('div', { class: 'ta' },
        h('button', { class: 'btn', type: 'button', disabled: S.busy, onclick() { send('em muốn gửi câu hỏi cho TA'); } }, icon('send'), 'Gửi câu hỏi cho TA'),
        h('span', { class: 'ta-eta' + (eta.late ? ' late' : '') }, eta.text)));
  }

  /* ---------- Cột phải: việc đang chờ + nháp FAQ ---------- */
  function renderSide() {
    const st = S.store || {};
    const acts = st.pending_actions || [];
    const sent = st.ta_queue || [];
    const ex = openEx();
    $('#pending-count').textContent = acts.length;
    const pending = acts.map((a) => h('div', { class: 'card is-pending' },
      h('div', { class: 'card-title' }, icon('send'), 'Câu hỏi soạn sẵn, chưa gửi'),
      h('div', { class: 'card-q' }, a.summary || a.question || ''),
      h('div', { class: 'card-meta' }, icon('clock'), a.on_duty ? 'TA đang trực, sẽ trả lời trong giờ trực' : 'TA trả lời từ ' + fmtWhen(a.ta_reply_time, S.now)),
      a.after_deadline ? h('div', { class: 'late-warn' }, icon('alert'),
        h('span', null, 'Sau hạn nộp' + (ex ? ' ' + shortTitle(ex.title) + ' (' + fmtWhen(ex.deadline, S.now) + ')' : '') + ': TA trả lời khi bài đã đóng. Gia hạn do giảng viên quyết định.')) : null,
      h('div', { class: 'card-actions' },
        h('button', { class: 'btn btn-primary btn-sm', type: 'button', onclick(e) { confirmAction(a, e.currentTarget); } }, 'Xác nhận gửi TA'),
        h('button', { class: 'btn btn-sm', type: 'button', onclick(e) { cancelAction(a, e.currentTarget); } }, 'Huỷ'))));
    const done = sent.map((q) => h('div', { class: 'card is-done' },
      h('div', { class: 'card-title' }, icon('check'), 'Đã gửi TA'),
      h('div', { class: 'card-q' }, q.question || q.summary || ''),
      h('div', { class: 'card-meta' }, icon('clock'), q.on_duty ? 'TA đang trực' : 'TA trả lời từ ' + fmtWhen(q.ta_reply_time, S.now), q.after_deadline ? h('span', { class: 'badge danger' }, 'sau hạn nộp') : null)));
    $('#pending').replaceChildren(...(pending.length || done.length ? [...pending, ...done]
      : [h('div', { class: 'none' }, 'Chưa có gì cần bạn duyệt. Trợ lý chỉ soạn sẵn câu hỏi, bạn bấm xác nhận thì mới gửi TA.')]));

    const fl = new Set(flagged());
    const faqs = st.faq || [];
    $('#faq-count').textContent = faqs.length;
    $('#faq').replaceChildren(...(faqs.length ? faqs.map((f) => {
      const locked = (f.section_refs || []).filter((r) => fl.has(r));
      const statusBadge = {
        draft: h('span', { class: 'badge accent' }, 'Bản nháp riêng tư'),
        pending_review: h('span', { class: 'badge warn' }, icon('clock'), 'Đang chờ giảng viên duyệt'),
        published: h('span', { class: 'badge ok' }, icon('check'), 'Đã đăng cho cả lớp'),
        rejected: h('span', { class: 'badge' }, 'Không được duyệt'),
      }[f.status] || h('span', { class: 'badge' }, f.status);
      return h('div', { class: 'card' + (f.status === 'draft' ? '' : ' is-done') },
        h('div', { class: 'card-meta' }, statusBadge, h('span', { class: 'badge' }, icon('hide'), 'ẩn danh')),
        h('div', { class: 'card-q' }, f.question),
        h('div', { class: 'card-a' }, f.answer),
        (f.section_refs || []).length ? h('div', { class: 'card-meta' }, (f.section_refs || []).map((r) => secChip(r, null, fl.has(r)))) : null,
        locked.length ? h('div', { class: 'fine' }, '🔒 ' + locked.join(', ') + ' đang bị gắn cờ nên chưa gửi duyệt được.') : null,
        f.status === 'draft' ? h('div', { class: 'card-actions' },
          h('button', { class: 'btn btn-danger btn-sm', type: 'button', onclick(e) { deleteDraft(f, e.currentTarget); } }, icon('trash'), 'Xoá nháp')) : null,
        f.status === 'draft' ? h('div', { class: 'fine' }, 'Chỉ bạn và người duyệt thấy bản này. Giảng viên/TA duyệt thì mới đăng.') : null);
    }) : [h('div', { class: 'none' }, 'Chưa có nháp. Trợ lý không tự đăng FAQ: chỉ soạn nháp ẩn danh, bạn xoá được bất cứ lúc nào.')]));
  }
  function secChip(sec, title, isFlagged, quote) {
    return h('button', { class: 'sec-chip' + (isFlagged ? ' is-flagged' : ''), type: 'button', title: quote || 'Xem ' + sec + ' trong tài liệu', onclick() { focusSection(sec); } },
      isFlagged ? icon('alert') : null, h('b', null, sec), title || null);
  }

  async function confirmAction(a, btn) {
    btn.disabled = true;
    try {
      const res = await Api.confirm(a.id, S.sid);
      const item = (res && res.ta_queue_item) || a;
      const late = item.after_deadline != null ? item.after_deadline : a.after_deadline;
      sysLine('ok', 'check', 'Đã gửi câu hỏi vào hàng chờ TA. ' + (a.on_duty ? 'TA đang trực.' : 'TA trả lời từ ' + fmtWhen(item.ta_reply_time || a.ta_reply_time, S.now) + (late ? ', sau hạn nộp.' : '.')));
      await poll();
    } catch (e) { btn.disabled = false; toast('Chưa gửi được, bạn thử lại nhé.'); }
  }
  async function cancelAction(a, btn) {
    btn.disabled = true;
    try { await Api.cancel(a.id, S.sid); sysLine('', 'x', 'Đã huỷ câu hỏi soạn sẵn. Chưa có gì được gửi cho TA.'); await poll(); }
    catch (e) { btn.disabled = false; toast('Chưa huỷ được, bạn thử lại nhé.'); }
  }
  async function deleteDraft(f, btn) {
    btn.disabled = true;
    try { await Api.faqDelete(f.id); toast('Đã xoá bản nháp FAQ.'); await poll(); }
    catch (e) { btn.disabled = false; toast('Chưa xoá được, bạn thử lại nhé.'); }
  }

  /* ---------- Tin nhắn ---------- */
  const box = () => $('#messages');
  function append(el) {
    const empty = $('.empty', box());
    if (empty) empty.remove();
    box().append(el);
    box().scrollTop = box().scrollHeight;
    annot.refresh();
    return el;
  }
  function sysLine(kind, ic, text, extra) {
    return append(h('div', { class: 'msg msg-sys ' + (kind || '') }, icon(ic), h('span', null, text, extra || null)));
  }
  function emptyState() {
    box().replaceChildren(h('div', { class: 'empty' }, icon('bot'), h('b', null, 'Kẹt chỗ nào trong buổi 3?'),
      h('span', null, 'Hỏi mình bằng lời của bạn. Câu trả lời nào cũng kèm mã mục để bạn tự đối chiếu với tài liệu bên trái.')));
  }

  function renderAssistant(r) {
    const key = CONF[r.confidence] ? r.confidence : 'no_source';
    const conf = CONF[key];
    const cites = r.citations || [];
    const events = r.events || [];
    const fl = new Set(flagged());
    events.forEach((e) => { if (e.type === 'flag_created' && e.data && e.data.section) fl.add(e.data.section); });
    const flCites = cites.filter((c) => fl.has(c.section)).map((c) => c.section);

    const why = {
      grounded: cites.length ? 'Dựa trên ' + cites.map((c) => c.section).join(', ') : 'Dựa trên tài liệu của khoá',
      flagged: (flCites.length ? flCites.join(', ') : 'Mục được trích') + ' đang bị gắn cờ, đọc kèm lưu ý bên dưới',
      no_source: 'Không trích được mục nào của tài liệu',
      refused: 'Câu trả lời bị chặn hoặc từ chối theo luật của khoá',
    }[key];

    /* Banner: ghi chú từ server; nếu server tính "flagged" mà không kèm ghi chú thì tự dựng một banner. */
    const notes = (r.notes || []).slice();
    if (key === 'flagged' && !notes.some((n) => n.type === 'warning')) {
      notes.unshift({ type: 'warning', text: (flCites.length ? flCites.join(', ') : 'Mục được trích') + ' đang bị gắn cờ cần xem lại. Đối chiếu phản ví dụ trước khi dùng câu này.' });
    }
    const flagCall = (r.trace || []).find((t) => t.tool === 'bao_loi_tai_lieu' && t.args && (t.args.claim || t.args.counterexample));
    const alerts = notes.map((n) => {
      const type = ['warning', 'blocked', 'info'].includes(n.type) ? n.type : 'info';
      return h('div', { class: 'note note-' + type, role: type === 'info' ? null : 'alert' }, icon({ warning: 'alert', blocked: 'shield', info: 'bulb' }[type]), h('span', null, String(n.text || '').replace(/^⚠️?\s*/, '')));
    });
    if (flagCall) {
      alerts.push(h('dl', { class: 'counter' },
        flagCall.args.claim ? [h('dt', null, 'Câu cần xem lại' + (flagCall.args.section ? ' ở ' + flagCall.args.section : '')), h('dd', null, '“' + flagCall.args.claim + '”')] : null,
        flagCall.args.counterexample ? [h('dt', null, 'Phản ví dụ đã gửi giảng viên'), h('dd', null, flagCall.args.counterexample)] : null));
    }

    const shownEvents = events.filter((e) => e.type !== 'tool_call');
    const steps = (r.trace || []);

    const foot = h('div', { class: 'msg-foot' });
    const fbBtn = h('button', { class: 'btn btn-ghost btn-sm', type: 'button', 'data-hax': '6', onclick() { openFeedback(r, foot, fbBtn); } }, icon('msg'), 'Báo sai');
    foot.append(fbBtn);
    if (steps.length) {
      foot.append(h('details', { class: 'trace' },
        h('summary', null, 'Trợ lý đã làm ' + steps.length + ' bước'),
        h('ol', null, steps.map((t) => h('li', null, h('code', null, t.tool), ' ',
          h('span', { class: 'args' }, shortArgs(t.args)), t.result_summary ? [h('br'), '→ ' + t.result_summary] : null)))));
    }

    return h('article', { class: 'msg msg-ai conf-' + key, 'data-mid': r.message_id || '' },
      h('div', { class: 'msg-head' },
        h('span', { class: 'conf', 'data-hax': '3', title: 'Độ chắc do hệ thống tính từ kết quả tra cứu thật của lượt này, không phải AI tự khai.' }, icon(conf.icon), conf.label),
        h('span', { class: 'conf-why' }, why)),
      h('div', { class: 'msg-body', 'data-hax': '4', html: rich(r.reply) }),
      alerts.length ? h('div', { class: 'msg-alerts', 'data-hax': '5' }, alerts) : null,
      cites.length ? h('div', { class: 'cites', 'data-hax': '2' }, h('span', { class: 'cites-label' }, 'Nguồn:'),
        cites.map((c) => secChip(c.section, c.title, fl.has(c.section), c.quote))) : null,
      shownEvents.length ? h('div', { class: 'events' }, shownEvents.map((e) => {
        const def = EVENTS[e.type] || ['bulb', e.type];
        return h('div', { class: 'ev ' + e.type }, icon(def[0]), h('span', null, e.text || def[1]));
      })) : null,
      foot);
  }
  function shortArgs(args) {
    const s = JSON.stringify(args || {});
    return s === '{}' ? '' : (s.length > 140 ? s.slice(0, 137) + '…' : s);
  }

  /* Nút "Báo sai" (G15): mở form ngắn, gửi /api/feedback, hiện mã ticket khi server xác nhận */
  function openFeedback(r, foot, btn) {
    if ($('.fb-form', foot)) return;
    const ta = h('textarea', { placeholder: 'Sai ở đâu? Ví dụ: trích nhầm mục, giải thích khác tài liệu…', 'aria-label': 'Nội dung phản ánh' });
    const form = h('form', { class: 'fb-form', async onsubmit(e) {
      e.preventDefault();
      const text = ta.value.trim();
      if (!text) { ta.focus(); return; }
      try {
        const res = await Api.feedback(S.sid, r.message_id, text);
        const id = res && (res.ticket_id || (res.ticket && res.ticket.id) || res.id);
        form.replaceWith(h('div', { class: 'fb-done' }, icon('check'), 'Đã ghi nhận phản ánh' + (id ? ' với mã ' + tkLabel(id) : '') + '. Giảng viên sẽ xem, tên bạn không được gửi kèm.'));
        btn.disabled = true;
        poll();
      } catch (err) { toast('Chưa gửi được phản ánh, bạn thử lại nhé.'); }
    } }, ta, h('div', null, h('button', { class: 'btn btn-primary btn-sm', type: 'submit' }, 'Gửi phản ánh'),
      h('button', { class: 'btn btn-sm', type: 'button', onclick() { form.remove(); } }, 'Thôi')));
    foot.append(form);
    ta.focus();
  }

  /* ---------- Gửi tin ---------- */
  async function send(text) {
    text = String(text || '').trim();
    if (!text || S.busy || !S.sid) return;
    S.busy = true;
    setBusy();
    append(h('div', { class: 'msg msg-user' }, text));
    const typing = append(h('div', { class: 'typing' }, h('span', { class: 'dots' }, h('i'), h('i'), h('i')), 'Đang tra tài liệu…'));
    try {
      let r;
      try { r = await Api.chat(S.sid, text); }
      catch (e) {
        if (e.status !== 404) throw e; // server khởi động lại: mở phiên mới rồi gửi lại một lần
        const s = await Api.session(S.now);
        S.sid = s.session_id;
        r = await Api.chat(S.sid, text);
      }
      typing.remove();
      if (r.hint_progress && r.hint_progress.max) S.hint = { level: r.hint_progress.level, max: r.hint_progress.max };
      append(renderAssistant(r));
      await poll();
    } catch (e) {
      typing.remove();
      const llm = e.status === 503;
      sysLine('err', 'alert', llm ? 'Trợ lý đang không kết nối được với AI. Tin của bạn chưa được trả lời. ' : 'Không gửi được tin (máy chủ không phản hồi). ',
        MOCK ? null : h('span', null, 'Xem bản đã lưu: ', REPLAYS.map((k, i) => [i ? ' · ' : '', h('a', { href: 'index.html?mock=' + k }, k)])));
    } finally {
      S.busy = false;
      setBusy();
    }
  }
  function setBusy() {
    $('#send').disabled = S.busy;
    renderQuick();
    annot.refresh();
  }

  /* ---------- Đồng bộ trạng thái (2 giây một lần, để thấy TA/GV thao tác) ---------- */
  async function poll() {
    try { S.store = await Api.state(); setConn(true); }
    catch (e) { setConn(false); return; }
    const key = JSON.stringify(S.store);
    if (key === S.storeKey) return;
    S.storeKey = key;
    renderSide();
    renderDocs();
    annot.refresh();
  }

  /* ---------- Khởi động / đổi giờ demo ---------- */
  async function restart(now) {
    try {
      const s = await Api.session(now || undefined);
      S.sid = s.session_id;
      S.now = s.now;
      S.course = await Api.course(S.sid);
      setConn(true);
    } catch (e) {
      setConn(false);
      box().replaceChildren();
      sysLine('err', 'alert', 'Chưa kết nối được máy chủ. Chạy "uvicorn app.main:app --port 8000" trong prototype/backend rồi tải lại trang.');
      return false;
    }
    S.hint = { level: 0, max: 3 };
    S.storeKey = '';
    S.activeSec = null;
    const clock = $('#clock');
    if (clock) clock.value = String(S.now).slice(0, 16);
    emptyState();
    renderPin();
    renderOutline();
    renderDocs();
    renderQuick();
    await poll();
    renderSide();
    annot.refresh();
    return true;
  }

  async function autoplay() {
    let rp;
    try { rp = await Api.loadReplay(); } catch (e) { return; }
    for (const turn of rp.turns || []) {
      await sleep(600);
      await send(turn.user);
    }
  }

  async function init() {
    window.App.mountTopbar('student', { onClock: (iso) => restart(iso) });

    $('#starters').replaceChildren(h('span', { class: 'starters-label' }, 'TIN MỒI'),
      ...STARTERS.map(([k, label, text]) => h('button', { class: 'starter', type: 'button', title: text, onclick() {
        const input = $('#input');
        input.value = text;
        input.dispatchEvent(new Event('input'));
        input.focus();
      } }, h('b', null, k), ' ' + label)));

    const input = $('#input');
    input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight + 2, 130) + 'px'; });
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); $('#composer').requestSubmit(); } });
    $('#composer').addEventListener('submit', (e) => {
      e.preventDefault();
      const text = input.value;
      if (!text.trim() || S.busy) return;
      input.value = '';
      input.style.height = 'auto';
      send(text);
    });
    box().addEventListener('click', (e) => {
      const ref = e.target.closest('.sec-ref');
      if (ref) focusSection(ref.dataset.sec);
    });

    if (MOCK) {
      const b = $('#mock-banner');
      b.hidden = false;
      b.replaceChildren(icon('play'), 'Đang phát lại bản đã lưu' + (REPLAYS.includes(MOCK) ? ' ' + MOCK : '') + '. Không gọi AI, mọi thao tác chỉ lưu trên trình duyệt này.',
        h('a', { href: 'index.html' }, 'Chat với AI thật'));
    }

    const ok = await restart();
    setInterval(poll, 2000);
    if (ok && MOCK) autoplay();
  }

  init();
})();
