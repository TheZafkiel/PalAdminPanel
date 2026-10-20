(() => {
  const menuButton = document.querySelector('.menu-button');
  const sidebar = document.querySelector('.sidebar');
  if (menuButton && sidebar) {
    menuButton.addEventListener('click', () => {
      const open = sidebar.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', (event) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(event.target) && !menuButton.contains(event.target)) {
        sidebar.classList.remove('open');
        menuButton.setAttribute('aria-expanded', 'false');
      }
    });
  }

  document.querySelectorAll('.confirm-form').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const message = form.dataset.confirm || '确定执行此操作吗？';
      if (!window.confirm(message)) {
        event.preventDefault();
        return;
      }
      const confirmation = form.querySelector('input[name="confirmation"]');
      if (confirmation) confirmation.value = 'BAN';
    });
  });

  document.querySelectorAll('.player-filter').forEach((filter) => {
    const select = document.getElementById(filter.dataset.target);
    if (!select) return;
    const options = Array.from(select.options);
    const count = document.querySelector(`.player-count[data-for="${select.id}"]`);
    const render = () => {
      const terms = filter.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      const matches = options.filter((option) => {
        const haystack = (option.dataset.search || option.textContent || '').toLocaleLowerCase();
        return terms.every((term) => haystack.includes(term));
      });
      select.replaceChildren(...matches);
      if (matches.length) matches[0].selected = true;
      if (count) count.textContent = `匹配 ${matches.length} / 全部 ${options.length}`;
    };
    filter.addEventListener('input', render);
    render();
  });

  document.querySelectorAll('.catalog-browser').forEach((browser) => {
    const filter = browser.querySelector('.catalog-filter');
    const category = browser.querySelector('.catalog-category');
    const input = document.getElementById(browser.dataset.input);
    const cards = Array.from(browser.querySelectorAll('.catalog-card'));
    const count = browser.querySelector('.catalog-count');
    const empty = browser.querySelector('.catalog-empty');
    if (!filter || !category || !input) return;

    const selectCard = (card) => {
      cards.forEach((candidate) => {
        const selected = candidate === card;
        candidate.classList.toggle('selected', selected);
        candidate.setAttribute('aria-selected', String(selected));
      });
      input.value = card?.dataset.value || '';
    };
    const render = () => {
      const terms = filter.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      const selectedCategory = category.value.toLocaleLowerCase();
      const visible = cards.filter((card) => {
        const haystack = (card.dataset.search || card.textContent || '').toLocaleLowerCase();
        const categories = (card.dataset.category || '').toLocaleLowerCase().split('|').filter(Boolean);
        const matchesSearch = terms.every((term) => haystack.includes(term));
        const matchesCategory = !selectedCategory || categories.includes(selectedCategory);
        card.hidden = !(matchesSearch && matchesCategory);
        return !card.hidden;
      });
      const current = cards.find((card) => card.classList.contains('selected') && !card.hidden);
      if (!current) selectCard(visible[0] || null);
      if (count) count.textContent = `显示 ${visible.length} / 全部 ${cards.length}`;
      if (empty) empty.hidden = visible.length > 0;
    };
    cards.forEach((card) => card.addEventListener('click', () => selectCard(card)));
    filter.addEventListener('input', render);
    category.addEventListener('change', render);
    render();
  });

  document.querySelectorAll('.catalog-filter[data-target]').forEach((filter) => {
    const select = document.getElementById(filter.dataset.target);
    if (!select) return;
    const options = Array.from(select.options);
    const count = document.querySelector(`.catalog-count[data-for="${select.id}"]`);
    const render = () => {
      const terms = filter.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      const matches = options.filter((option) => {
        const haystack = (option.dataset.search || option.textContent || '').toLocaleLowerCase();
        return terms.every((term) => haystack.includes(term));
      });
      select.replaceChildren(...matches);
      if (matches.length) matches[0].selected = true;
      if (count) count.textContent = `显示 ${matches.length} / 全部 ${options.length}`;
    };
    filter.addEventListener('input', render);
    render();
  });

  document.querySelectorAll('.async-grant-form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const resultBox = form.querySelector('.inline-action-result');
      const originalText = button ? button.textContent : '';
      if (button) {
        button.disabled = true;
        button.textContent = '正在提交…';
      }
      if (resultBox) {
        resultBox.className = 'inline-action-result pending';
        resultBox.textContent = '正在等待服务器返回…';
      }
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const payload = await response.json();
        if (resultBox) {
          resultBox.className = `inline-action-result ${payload.success ? 'success' : 'error'}`;
          resultBox.textContent = `${new Date().toLocaleTimeString()} · ${payload.message || '服务器未返回内容'}`;
        }
      } catch (error) {
        if (resultBox) {
          resultBox.className = 'inline-action-result error';
          resultBox.textContent = `提交失败：${error.message || '无法读取服务器响应'}`;
        }
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = originalText;
        }
      }
    });
  });

  const commandForm = document.querySelector('.command-form');
  if (commandForm) {
    const filter = commandForm.querySelector('.command-filter');
    const select = commandForm.querySelector('.command-select');
    const meta = commandForm.querySelector('.command-meta');
    const argumentsInput = commandForm.querySelector('.command-arguments');
    const confirmation = commandForm.querySelector('input[name="confirmation"]');
    const options = select ? Array.from(select.options) : [];
    const updateMeta = () => {
      const option = select && select.selectedOptions[0];
      if (!option || !meta) return;
      const readOnly = option.dataset.readOnly === 'true';
      const count = option.dataset.argumentCount || '0';
      const title = option.dataset.title || '服务器指令';
      const syntax = option.dataset.syntax || option.value;
      const detail = option.dataset.detail || '';
      meta.textContent = `${title}\n用法：${syntax}\n${detail}\n${readOnly ? '只读查询' : '修改类指令（二次确认）'} · 服务器公布的必填参数数：${count}`;
      meta.classList.toggle('danger-text', !readOnly);
      if (argumentsInput) argumentsInput.placeholder = `用法：${syntax}`;

      const eggBuilder = commandForm.querySelector('.egg-builder');
      if (eggBuilder) eggBuilder.hidden = !['giveegg', 'givemeegg'].includes(option.value);
    };
    const render = () => {
      if (!select || !filter) return;
      const query = filter.value.trim().toLocaleLowerCase();
      const matches = options.filter((option) => (option.dataset.search || '').toLocaleLowerCase().includes(query));
      select.replaceChildren(...matches);
      if (matches.length) matches[0].selected = true;
      updateMeta();
    };
    if (filter) filter.addEventListener('input', render);
    if (select) select.addEventListener('change', updateMeta);
    const eggButton = commandForm.querySelector('.build-egg-arguments');
    if (eggButton) eggButton.addEventListener('click', () => {
      const command = select?.value || '';
      const player = commandForm.querySelector('.egg-player')?.value || '';
      const egg = commandForm.querySelector('.egg-id')?.value || '';
      const pal = commandForm.querySelector('.egg-pal')?.value || '';
      const level = commandForm.querySelector('.egg-level')?.value || '1';
      if (argumentsInput) argumentsInput.value = command === 'giveegg'
        ? `${player} ${egg} ${pal} ${level}`.trim()
        : `${egg} ${pal} ${level}`.trim();
      argumentsInput?.focus();
    });
    const addCommandRecord = (payload) => {
      const history = document.getElementById('command-history');
      if (!history) return;
      const empty = history.querySelector('.command-history-empty');
      if (empty) empty.remove();
      const article = document.createElement('article');
      article.className = `command-record ${payload.success ? 'success' : 'error'}`;
      const heading = document.createElement('div');
      const timestamp = document.createElement('time');
      timestamp.textContent = payload.timestamp || new Date().toLocaleString();
      const status = document.createElement('span');
      status.textContent = payload.success ? '成功' : '失败';
      heading.append(timestamp, status);
      const command = document.createElement('code');
      command.textContent = `> ${payload.command || ''}`;
      const result = document.createElement('pre');
      result.textContent = payload.result || payload.message || '服务器未返回内容';
      article.append(heading, command, result);
      history.prepend(article);
      while (history.children.length > 80) history.lastElementChild.remove();
      const count = document.querySelector('.history-count');
      if (count) count.textContent = `最近 ${history.children.length} 条`;
    };
    commandForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const option = select && select.selectedOptions[0];
      if (!option) return;
      if (confirmation) confirmation.value = '';
      if (option.dataset.readOnly !== 'true') {
        const approved = window.confirm(`确定执行 ${option.value} 吗？此指令可能修改服务器数据，部分操作无法撤销。`);
        if (!approved) return;
        if (confirmation) confirmation.value = 'EXECUTE';
      }
      const button = commandForm.querySelector('button[type="submit"]');
      const originalText = button ? button.textContent : '';
      if (button) {
        button.disabled = true;
        button.textContent = '正在执行…';
      }
      const commandLine = `${option.value} ${argumentsInput ? argumentsInput.value.trim() : ''}`.trim();
      try {
        const response = await fetch(commandForm.action, {
          method: 'POST',
          body: new FormData(commandForm),
          headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const payload = await response.json();
        addCommandRecord({...payload, command: payload.command || commandLine});
      } catch (error) {
        addCommandRecord({
          success: false,
          command: commandLine,
          result: `请求失败：${error.message || '无法读取服务器响应'}`
        });
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = originalText;
        }
      }
    });
    render();
  }

  const showCopyToast = (message) => {
    const toast = document.querySelector('.copy-toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    window.setTimeout(() => toast.classList.remove('show'), 1800);
  };
  const copyText = async (value) => {
    try {
      await navigator.clipboard.writeText(value);
      showCopyToast(`已复制：${value}`);
    } catch (_error) {
      const input = document.createElement('textarea');
      input.value = value;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      input.remove();
      showCopyToast(`已复制：${value}`);
    }
  };
  document.addEventListener('click', (event) => {
    const copy = event.target.closest('.copy-value');
    if (copy) copyText(copy.dataset.value || '');
    const selected = event.target.closest('.copy-selected');
    if (selected) {
      const select = document.getElementById(selected.dataset.target);
      if (select && select.value) copyText(select.value);
    }
    const insert = event.target.closest('.insert-value');
    if (insert) {
      const input = document.querySelector(insert.dataset.target);
      if (input) {
        const start = input.selectionStart ?? input.value.length;
        const before = input.value.slice(0, start).trimEnd();
        const after = input.value.slice(input.selectionEnd ?? start).trimStart();
        input.value = [before, insert.dataset.value, after].filter(Boolean).join(' ');
        input.focus();
      }
    }
  });
  document.querySelectorAll('.quick-filter').forEach((filter) => {
    const container = document.getElementById(filter.dataset.container);
    if (!container) return;
    filter.addEventListener('input', () => {
      const terms = filter.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
      container.querySelectorAll('.quick-choice').forEach((row) => {
        const text = (row.dataset.search || '').toLocaleLowerCase();
        row.hidden = !terms.every((term) => text.includes(term));
      });
    });
  });
  const ingameFilter = document.querySelector('.ingame-command-filter');
  if (ingameFilter) ingameFilter.addEventListener('input', () => {
    const terms = ingameFilter.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    document.querySelectorAll('.ingame-command-card').forEach((card) => {
      const text = (card.dataset.search || '').toLocaleLowerCase();
      card.hidden = !terms.every((term) => text.includes(term));
    });
  });
  document.querySelectorAll('.copy-ingame-command').forEach((button) => {
    button.addEventListener('click', () => {
      const card = button.closest('.ingame-command-card');
      const player = document.querySelector('.ingame-player')?.value || '';
      let command = card?.dataset.template || '';
      if (player) command = command.replace(/<UserId1?>/g, player);
      copyText(command);
    });
  });

})();
