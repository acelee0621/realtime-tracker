class InventoryApp {
    constructor() {
        this.websocket = null;
        this.inventoryItems = new Map();
        this.isConnected = false;
        this.pendingUpdates = new Set();
        this.init();
    }
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadInitialData();
    }
    setupEventListeners() {
        const form = document.getElementById('add-item-form');
        form.addEventListener('submit', (e) => this.handleAddItem(e));
    }
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        this.websocket = new WebSocket(wsUrl);
        this.websocket.onopen = () => {
            this.updateConnectionStatus(true);
        };
        this.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        this.websocket.onclose = () => {
            this.updateConnectionStatus(false);
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connection-status');
        if (connected) {
            statusElement.className = 'status connected';
            statusElement.textContent = '🟢 已连接服务器';
        } else {
            statusElement.className = 'status disconnected';
            statusElement.textContent = '🔴 已断开与服务器的连接';
        }
    }
    async loadInitialData() {
        try {
            const response = await fetch('/api/inventory');
            if (response.ok) {
                const items = await response.json();
                this.inventoryItems.clear();
                items.forEach(item => {
                    this.inventoryItems.set(item.id, item);
                });
                this.renderInventory();
            }
        } catch (error) {
            this.showError('Failed to load inventory data');
        }
    }
    handleWebSocketMessage(data) {
        const {event, data: itemData} = data;
        switch (event) {
            case 'INSERT':
                this.inventoryItems.set(itemData.id, itemData);
                this.renderInventory();
                this.showNotification(`已添加: ${itemData.name}`, 'success');
                break;
            case 'UPDATE':
                this.inventoryItems.set(itemData.id, itemData);
                this.renderInventory();
                this.showNotification(`已更新: ${itemData.name}`, 'info');
                break;
            case 'DELETE':
                this.inventoryItems.delete(itemData.id);
                this.renderInventory();
                this.showNotification(`已删除: ${itemData.name}`, 'warning');
                break;
            default:
                break;
        }
    }
    async handleAddItem(event) {
        event.preventDefault();
        const nameInput = document.getElementById('item-name');
        const quantityInput = document.getElementById('item-quantity');
        const name = nameInput.value.trim();
        const quantity = parseInt(quantityInput.value);
        if (!name || quantity < 0) {
            this.showError('请输入合法的物品名称与数量');
            return;
        }
        try {
            const response = await fetch('/api/inventory', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, quantity}),
            });
            if (response.ok) {
                nameInput.value = '';
                quantityInput.value = '';
            } else {
                const error = await response.json();
                this.showError(error.detail || '添加物品失败');
            }
        } catch (error) {
            this.showError('添加物品失败');
        }
    }
    async updateItemQuantity(id, newQuantity) {
        if (this.pendingUpdates.has(id)) return;
        this.pendingUpdates.add(id);
        const item = this.inventoryItems.get(id);
        if (item) {
            const originalQuantity = item.quantity;
            item.quantity = newQuantity;
            this.renderInventory();
            try {
                const response = await fetch(`/api/inventory/${id}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({quantity: newQuantity}),
                });
                if (!response.ok) {
                    item.quantity = originalQuantity;
                    this.renderInventory();
                    const error = await response.json();
                    this.showError(error.detail || '更新物品失败');
                }
            } catch (error) {
                item.quantity = originalQuantity;
                this.renderInventory();
                this.showError('更新物品失败');
            } finally {
                this.pendingUpdates.delete(id);
            }
        }
    }
    async deleteItem(id) {
        if (!confirm('确认要删除这个物品吗?')) return;
        const itemElement = document.querySelector(`[data-item-id="${id}"]`);
        if (itemElement) itemElement.style.opacity = '0.5';
        try {
            const response = await fetch(`/api/inventory/${id}`, {method: 'DELETE'});
            if (!response.ok) {
                if (itemElement) itemElement.style.opacity = '1';
                const error = await response.json();
                this.showError(error.detail || '删除物品失败');
            }
        } catch (error) {
            if (itemElement) itemElement.style.opacity = '1';
            this.showError('删除物品失败');
        }
    }
    renderInventory() {
        const container = document.getElementById('inventory-container');
        if (this.inventoryItems.size === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>库存为空</h3>
                    <p>请使用上方表单添加首个商品！</p>
                </div>
            `;
            return;
        }
        const sortedItems = Array.from(this.inventoryItems.values())
            .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
        container.innerHTML = sortedItems.map(item => this.renderInventoryItem(item)).join('');
    }
    renderInventoryItem(item) {
        const updatedAt = new Date(item.updated_at).toLocaleString();
        const isUpdating = this.pendingUpdates.has(item.id);
        return `
            <div class="inventory-item ${isUpdating ? 'updating' : ''}" data-item-id="${item.id}">
                <div class="item-info">
                    <div class="item-name">${this.escapeHtml(item.name)}</div>
                    <div class="item-meta">最后更新: ${updatedAt}</div>
                </div>
                <div class="item-actions">
                    <input
                        type="number"
                        class="quantity-input"
                        value="${item.quantity}"
                        min="0"
                        onchange="app.updateItemQuantity(${item.id}, parseInt(this.value))"
                        ${isUpdating ? 'disabled' : ''}
                    >
                    <button
                        class="btn btn-danger btn-small"
                        onclick="app.deleteItem(${item.id})"
                        ${isUpdating ? 'disabled' : ''}
                    >
                        删除
                    </button>
                </div>
            </div>
        `;
    }
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;
        switch (type) {
            case 'success':
                notification.style.background = '#28a745';
                break;
            case 'warning':
                notification.style.background = '#ffc107';
                notification.style.color = '#212529';
                break;
            case 'error':
                notification.style.background = '#dc3545';
                break;
            default:
                notification.style.background = '#17a2b8';
        }
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    showError(message) {
        this.showNotification(message, 'error');
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the app
const app = new InventoryApp();