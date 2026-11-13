/* staff.js — trang TA (ta.html) và Giảng viên (gv.html). Làm mới mỗi 2 giây qua /api/state.
   Thiết kế cố ý: không trang nào liệt kê học viên đã xin đáp án (spec §3.2: không "méc"). */
(function () {
  'use strict';
  const { $, h, icon, Api, Live, fmtWhen, toast, annot, setConn } = window.App;
  const page = document.body.dataset.page;
  let store = null, storeKey = '', docs = {}, now = null;

  const tkLabel = (id) => '#' + String(id || '').replace(/^#/, '');
  const chip = (sec, flagged) => h('span', { class: 'sec-chip' + (flagged ? ' is-flagged' : '') }, flagged ? icon('alert') : null, h('b', null, sec));
  const none = (text) => h('div', { class: 'none' }, text);

  async function act(fn, btn, okText) {
    btn.disabled = true;
    try { await fn(); if (okText) toast(okText); await poll(true); }
    catch (e) { btn.disabled = false; toast('Chưa thực hiện được, thử lại nhé.'); }
  }

  /* ---------- TA ---------- */
  function renderTA() {
    const queue = store.ta_queue || [];
    const faqs = store.faq || [];
    const review = faqs.filter((f) => f.status === 'pending_review');
    const handled = faqs.filter((f) => f.status === 'published' || f.status === 'rejected');
    const fl = new Set(store.flagged_sections || []);

    $('#tiles').replaceChildren(
      tile('Câu hỏi học viên đã xác nhận gửi', queue.length, 'Chỉ vào đây sau khi học viên bấm Xác nhận. Trợ lý không tự chuyển.', 'inbox'),
      tile('FAQ chờ bạn duyệt', review.length, 'Không bản nào tự đăng. Không ai duyệt thì bản nháp cứ nằm chờ.', 'file'),
      tile('Câu hỏi có câu trả lời sau hạn nộp', queue.filter((q) => q.after_deadline).length, 'Học viên đã được báo trước giờ trả lời thật.', 'clock'));

    $('#queue').replaceChildren(...(queue.length ? queue.map((q) => h('div', { class: 'card' },
      h('div', { class: 'card-meta' },
        h('span', { class: 'badge' }, icon('clock'), q.on_duty ? 'Trong giờ trực' : 'Trả lời từ ' + fmtWhen(q.ta_reply_time, now)),
        q.after_deadline ? h('span', { class: 'badge danger' }, icon('alert'), 'Sau hạn nộp') : h('span', { class: 'badge ok' }, 'Trước hạn nộp'),
        q.exercise_id ? h('span', { class: 'badge' }, String(q.exercise_id).replace('bt', 'Bài ')) : null),
      h('div', { class: 'card-q' }, q.question || q.summary || ''),
      q.ai_summary ? h('div', { class: 'ai-sum' }, icon('bot'), h('span', null, q.ai_summary)) : null))
      : [none('Chưa có câu hỏi nào. Học viên thấy giờ TA trả lời thật trước khi quyết định gửi.')]));

    $('#review').replaceChildren(...(review.length ? review.map((f) => {
      const refs = f.section_refs || [];
      const locked = refs.filter((r) => fl.has(r));
      return h('div', { class: 'card' },
        h('div', { class: 'card-meta' },
          h('span', { class: 'badge' }, icon('hide'), 'Đã ẩn danh'),
          h('span', { class: 'badge ok' }, icon('check'), 'Không chứa gợi ý bài đang mở'),
          locked.length ? h('span', { class: 'badge warn' }, icon('alert'), 'Có cờ nghi vấn: ' + locked.join(', ')) : h('span', { class: 'badge' }, 'Không có cờ nghi vấn')),
        h('dl', { class: 'kv' }, h('dt', null, 'Hỏi'), h('dd', null, f.question), h('dt', null, 'Đáp'), h('dd', null, f.answer),
          h('dt', null, 'Mã mục'), h('dd', null, refs.length ? h('span', { class: 'card-meta' }, refs.map((r) => chip(r, fl.has(r)))) : 'không trích mục nào')),
        locked.length ? h('div', { class: 'fine' }, '🔒 Mục ' + locked.join(', ') + ' đang chờ giảng viên xem lại. Đóng ticket ở trang Giảng viên rồi mới duyệt đăng được.') : null,
        h('div', { class: 'card-actions' },
          h('button', { class: 'btn btn-primary btn-sm', type: 'button', disabled: locked.length > 0, onclick(e) { act(() => Api.faqApprove(f.id), e.currentTarget, 'Đã duyệt. FAQ được đăng cho cả lớp.'); } }, icon('check'), 'Duyệt đăng'),
          h('button', { class: 'btn btn-sm', type: 'button', onclick(e) { act(() => Api.faqReject(f.id), e.currentTarget, 'Đã từ chối bản nháp.'); } }, icon('x'), 'Từ chối')));
    }) : [none('Không có bản nháp nào chờ duyệt.')]));

    $('#handled').replaceChildren(...(handled.length ? handled.map((f) => h('div', { class: 'card is-done' },
      h('div', { class: 'card-meta' }, f.status === 'published' ? h('span', { class: 'badge ok' }, icon('check'), 'Đã đăng') : h('span', { class: 'badge' }, 'Đã từ chối')),
      h('div', { class: 'card-q' }, f.question))) : [none('Chưa xử lý bản nào.')]));
  }

  /* ---------- Giảng viên ---------- */
  function renderGV() {
    const tickets = store.tickets || [];
    const open = tickets.filter((t) => t.status === 'open');
    const closed = tickets.filter((t) => t.status !== 'open');
    const fl = store.flagged_sections || [];
    const n = (store.stats && store.stats.bt3_hint_sessions) || 0;

    $('#tiles').replaceChildren(
      h('div', { class: 'tile hero' },
        h('span', { class: 'tile-label' }, 'Tối nay có'),
        h('span', { class: 'tile-value' }, n),
        h('span', { class: 'tile-label' }, 'lượt hỏi kẹt Bài 3'),
        h('span', { class: 'tile-note' }, icon('hide'), 'Số liệu gộp, không kèm tên. Trang này không liệt kê ai đã xin đáp án.')),
      tile('Ticket đang mở', open.length, 'Trợ lý tự gắn cờ ẩn danh, không cần ai cho phép.', 'flag'),
      tile('Mục đang khoá đăng FAQ', fl.length ? fl.join(', ') : '0', 'Mở khoá khi bạn đóng ticket của mục đó.', 'lock'));

    const card = (t) => {
      const isDoc = t.type !== 'feedback';
      return h('div', { class: 'card' + (t.status === 'open' ? '' : ' is-done') },
        h('div', { class: 'card-meta' },
          h('span', { class: 'tk-id' }, tkLabel(t.id)),
          h('span', { class: 'badge ' + (isDoc ? 'warn' : 'accent') }, icon(isDoc ? 'flag' : 'msg'), isDoc ? 'Nghi tài liệu có câu sai' : 'Học viên báo câu trả lời sai'),
          t.section ? chip(t.section, t.status === 'open' && isDoc) : null,
          h('span', { class: 'badge' }, icon('hide'), 'ẩn danh'),
          t.status === 'open' ? null : h('span', { class: 'badge ok' }, icon('check'), 'Đã đóng')),
        isDoc && docs[t.section] ? h('div', { class: 'quote' }, docs[t.section]) : null,
        h('dl', { class: 'kv' },
          t.claim ? [h('dt', null, 'Câu bị nghi'), h('dd', null, '“' + t.claim + '”')] : null,
          t.counterexample ? [h('dt', null, 'Phản ví dụ'), h('dd', null, t.counterexample)] : null,
          t.text ? [h('dt', null, 'Phản ánh'), h('dd', null, t.text)] : null,
          t.message_id ? [h('dt', null, 'Tin liên quan'), h('dd', null, t.message_id)] : null),
        t.status === 'open' && isDoc ? h('div', { class: 'fine' }, '🔒 Đang khoá mọi FAQ trích ' + t.section + ' cho tới khi bạn đóng ticket.') : null,
        t.status === 'open' ? h('div', { class: 'card-actions' },
          h('button', { class: 'btn btn-primary btn-sm', type: 'button', onclick(e) { act(() => Api.ticketClose(t.id), e.currentTarget, isDoc ? 'Đã đóng ticket và mở khoá FAQ của ' + t.section + '.' : 'Đã đóng ticket.'); } },
            icon('check'), isDoc ? 'Đóng ticket (mở khoá FAQ)' : 'Đóng ticket')) : null);
    };
    $('#tickets').replaceChildren(...(open.length ? open.map(card) : [none('Không có ticket nào đang mở. Khi trợ lý thấy một câu trong tài liệu có thể sai, ticket kèm phản ví dụ sẽ hiện ở đây ngay.')]));
    $('#closed').replaceChildren(...(closed.length ? closed.map(card) : [none('Chưa đóng ticket nào.')]));
  }

  function tile(label, value, note, ic) {
    return h('div', { class: 'tile' }, h('span', { class: 'tile-label' }, label), h('span', { class: 'tile-value' }, value), h('span', { class: 'tile-note' }, icon(ic), note));
  }

  async function poll(force) {
    try { store = await Api.state(); setConn(true); }
    catch (e) { setConn(false); return; }
    const key = JSON.stringify(store);
    if (key === storeKey && !force) return;
    storeKey = key;
    (page === 'ta' ? renderTA : renderGV)();
    annot.refresh();
  }

  async function init() {
    window.App.mountTopbar(page);
    try { // dữ liệu khoá chỉ để hiện nguyên văn mục tài liệu trong ticket; lỗi thì bỏ qua
      const s = await Live.session();
      now = s.now;
      const c = await Live.course(s.session_id);
      (c.docs || []).forEach((d) => { docs[d.section] = d.text; });
    } catch (e) { /* trang vẫn chạy được không cần dữ liệu khoá */ }
    await poll(true);
    setInterval(poll, 2000);
  }
  init();
})();
