class MarkdownRenderer {
    constructor() {
        this.initializeMarked();
    }

    initializeMarked() {
        if (typeof marked !== 'undefined') {
            // 配置 marked
            marked.setOptions({
                highlight: function(code, language) {
                    if (typeof hljs !== 'undefined' && language && hljs.getLanguage(language)) {
                        try {
                            return hljs.highlight(code, { language }).value;
                        } catch (__) {}
                    }
                    if (typeof hljs !== 'undefined') {
                        return hljs.highlightAuto(code).value;
                    }
                    return code;
                },
                breaks: true,
                gfm: true,
                sanitize: false
            });
        }
    }

    render(markdownText) {
        if (!markdownText || typeof marked === 'undefined') {
            return this.escapeHtml(markdownText || '');
        }
        
        try {
            return marked.parse(markdownText);
        } catch (error) {
            console.error('Markdown 渲染错误:', error);
            return this.escapeHtml(markdownText);
        }
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    renderResultContent(content) {
        if (this.isMarkdownContent(content)) {
            return this.createMarkdownContainer(content);
        } else {
            return `<div class="plain-text-result">${this.escapeHtml(content)}</div>`;
        }
    }

    createMarkdownContainer(content) {
        const toolbar = this.createToolbarHTML(content);
        const renderedContent = this.render(content);
        
        return `
            ${toolbar}
            <div class="markdown-content">${renderedContent}</div>
        `;
    }

    createToolbarHTML(content) {
        return `
            <div class="markdown-toolbar">
                <button onclick="markdownRenderer.copyToClipboard('${this.escapeForAttribute(content)}')">📋 复制</button>
                <button onclick="markdownRenderer.toggleFullscreen(this.parentNode.parentNode)">🔍 全屏</button>
            </div>
        `;
    }

    escapeForAttribute(text) {
        return text.replace(/'/g, '&#39;').replace(/"/g, '&quot;').replace(/\n/g, '\\n');
    }

    isMarkdownContent(text) {
        if (!text) return false;
        
        // 简单的 markdown 格式检测
        const markdownPatterns = [
            /^#+\s/m,           // 标题
            /\*\*.*?\*\*/,      // 粗体
            /\*.*?\*/,          // 斜体
            /```[\s\S]*?```/,   // 代码块
            /`.*?`/,            // 行内代码
            /^\s*[-*+]\s/m,     // 无序列表
            /^\s*\d+\.\s/m,     // 有序列表
            /^\s*>\s/m,         // 引用
            /\[.*?\]\(.*?\)/    // 链接
        ];
        
        return markdownPatterns.some(pattern => pattern.test(text));
    }

    copyToClipboard(text) {
        // 解码 HTML 实体
        const decodedText = text.replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/\\n/g, '\n');
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(decodedText).then(() => {
                this.showToast('内容已复制到剪贴板');
            }).catch(() => {
                this.fallbackCopyTextToClipboard(decodedText);
            });
        } else {
            this.fallbackCopyTextToClipboard(decodedText);
        }
    }

    fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showToast('内容已复制到剪贴板');
        } catch (err) {
            console.error('复制失败:', err);
            this.showToast('复制失败，请手动复制');
        }
        
        document.body.removeChild(textArea);
    }

    toggleFullscreen(element) {
        if (!element) return;
        
        element.classList.toggle('fullscreen-modal');
        
        if (element.classList.contains('fullscreen-modal')) {
            // 全屏模式
            const toolbar = element.querySelector('.markdown-toolbar button:last-child');
            if (toolbar) toolbar.textContent = '❌ 退出全屏';
        } else {
            // 退出全屏
            const toolbar = element.querySelector('.markdown-toolbar button:last-child');
            if (toolbar) toolbar.textContent = '🔍 全屏';
        }
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            z-index: 10000;
            font-size: 14px;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 2000);
    }
}

// 创建全局实例
const markdownRenderer = new MarkdownRenderer();
