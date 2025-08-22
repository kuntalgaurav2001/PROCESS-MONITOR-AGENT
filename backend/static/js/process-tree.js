/**
 * Process Tree Visualization Module
 * Handles the interactive process tree display
 */

class ProcessTreeVisualizer {
    constructor() {
        this.currentTreeData = null;
        this.expandedNodes = new Set();
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Global click handler for tree interactions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tree-toggle')) {
                this.toggleNode(e.target);
            } else if (e.target.classList.contains('process-details')) {
                this.showProcessDetails(e.target);
            }
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const focusedElement = document.activeElement;
                if (focusedElement.classList.contains('tree-toggle')) {
                    e.preventDefault();
                    this.toggleNode(focusedElement);
                }
            }
        });
    }
    
    renderTree(treeData, containerId = 'processTree') {
        this.currentTreeData = treeData;
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        // Add tree header
        const header = this.createTreeHeader();
        container.appendChild(header);
        
        // Render tree nodes
        treeData.forEach(node => {
            const treeNode = this.createTreeNode(node, 0);
            container.appendChild(treeNode);
        });
        
        // Restore expanded state
        this.restoreExpandedState();
    }
    
    createTreeHeader() {
        const header = document.createElement('div');
        header.className = 'tree-header mb-3';
        header.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <h6 class="mb-0">
                    <i class="fas fa-sitemap me-2"></i>Process Hierarchy
                </h6>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-secondary" onclick="processTreeVisualizer.expandAll()">
                        <i class="fas fa-expand-alt me-1"></i>Expand All
                    </button>
                    <button type="button" class="btn btn-outline-secondary" onclick="processTreeVisualizer.collapseAll()">
                        <i class="fas fa-compress-alt me-1"></i>Collapse All
                    </button>
                    <button type="button" class="btn btn-outline-secondary" onclick="processTreeVisualizer.resetView()">
                        <i class="fas fa-undo me-1"></i>Reset
                    </button>
                </div>
            </div>
            <small class="text-muted">Click on arrows to expand/collapse process trees</small>
        `;
        return header;
    }
    
    createTreeNode(node, level = 0) {
        const treeNode = document.createElement('div');
        treeNode.className = 'tree-node';
        treeNode.dataset.pid = node.process.pid;
        treeNode.dataset.level = level;
        
        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = this.expandedNodes.has(node.process.pid);
        const toggleIcon = hasChildren ? 'fas fa-chevron-right' : 'fas fa-circle';
        const toggleClass = hasChildren ? 'cursor-pointer' : 'text-muted';
        
        treeNode.innerHTML = `
            <div class="process-info">
                <div class="process-details">
                    <i class="tree-toggle ${toggleClass} ${isExpanded ? 'expanded' : ''}" 
                       data-pid="${node.process.pid}"
                       title="${hasChildren ? 'Click to expand/collapse' : 'No child processes'}">
                        <i class="${toggleIcon}"></i>
                    </i>
                    <div class="process-main-info">
                        <strong class="process-name">${this.escapeHtml(node.process.name)}</strong>
                        <span class="process-pid text-muted">(PID: ${node.process.pid})</span>
                        ${node.process.ppid ? `<span class="process-ppid text-muted">← PPID: ${node.process.ppid}</span>` : ''}
                    </div>
                </div>
                <div class="process-metrics">
                    <span class="badge bg-primary">CPU: ${node.process.cpu_percent.toFixed(1)}%</span>
                    <span class="badge bg-info">Memory: ${node.process.memory_rss_mb} MB</span>
                    <span class="badge bg-secondary">${node.process.status}</span>
                    ${hasChildren ? `<span class="badge bg-success">${node.children.length} children</span>` : ''}
                </div>
            </div>
            ${hasChildren ? `<div class="tree-children ${isExpanded ? '' : 'collapsed'}">${this.renderChildren(node.children, level + 1)}</div>` : ''}
        `;
        
        return treeNode;
    }
    
    renderChildren(children, level) {
        return children.map(child => {
            const childNode = this.createTreeNode(child, level);
            return childNode.outerHTML;
        }).join('');
    }
    
    toggleNode(toggleElement) {
        const pid = toggleElement.dataset.pid;
        const treeNode = toggleElement.closest('.tree-node');
        const children = treeNode.querySelector('.tree-children');
        const icon = toggleElement.querySelector('i');
        
        if (!children) return;
        
        if (children.classList.contains('collapsed')) {
            // Expand
            children.classList.remove('collapsed');
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-down');
            toggleElement.classList.add('expanded');
            this.expandedNodes.add(pid);
        } else {
            // Collapse
            children.classList.add('collapsed');
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
            toggleElement.classList.remove('expanded');
            this.expandedNodes.delete(pid);
        }
        
        // Animate the transition
        this.animateToggle(children);
    }
    
    animateToggle(element) {
        element.style.transition = 'all 0.3s ease-in-out';
        setTimeout(() => {
            element.style.transition = '';
        }, 300);
    }
    
    expandAll() {
        const nodes = document.querySelectorAll('.tree-node');
        nodes.forEach(node => {
            const toggle = node.querySelector('.tree-toggle');
            const children = node.querySelector('.tree-children');
            if (toggle && children && children.classList.contains('collapsed')) {
                this.toggleNode(toggle);
            }
        });
    }
    
    collapseAll() {
        const nodes = document.querySelectorAll('.tree-node');
        nodes.forEach(node => {
            const toggle = node.querySelector('.tree-toggle');
            const children = node.querySelector('.tree-children');
            if (toggle && children && !children.classList.contains('collapsed')) {
                this.toggleNode(toggle);
            }
        });
    }
    
    resetView() {
        this.expandedNodes.clear();
        this.renderTree(this.currentTreeData);
    }
    
    restoreExpandedState() {
        this.expandedNodes.forEach(pid => {
            const toggle = document.querySelector(`[data-pid="${pid}"]`);
            if (toggle) {
                const children = toggle.closest('.tree-node').querySelector('.tree-children');
                if (children && children.classList.contains('collapsed')) {
                    this.toggleNode(toggle);
                }
            }
        });
    }
    
    searchInTree(query) {
        if (!query.trim()) {
            this.resetSearch();
            return;
        }
        
        const nodes = document.querySelectorAll('.tree-node');
        nodes.forEach(node => {
            const processName = node.querySelector('.process-name').textContent.toLowerCase();
            const processPid = node.querySelector('.process-pid').textContent;
            
            if (processName.includes(query.toLowerCase()) || processPid.includes(query)) {
                node.style.display = 'block';
                node.classList.add('search-highlight');
                
                // Expand parent nodes to show search results
                this.expandToNode(node);
            } else {
                node.style.display = 'none';
                node.classList.remove('search-highlight');
            }
        });
    }
    
    expandToNode(targetNode) {
        let parent = targetNode.parentElement;
        while (parent && parent.classList.contains('tree-children')) {
            parent.classList.remove('collapsed');
            const toggle = parent.previousElementSibling.querySelector('.tree-toggle');
            if (toggle) {
                toggle.classList.add('expanded');
                const icon = toggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-chevron-right');
                    icon.classList.add('fa-chevron-down');
                }
            }
            parent = parent.parentElement;
        }
    }
    
    resetSearch() {
        const nodes = document.querySelectorAll('.tree-node');
        nodes.forEach(node => {
            node.style.display = 'block';
            node.classList.remove('search-highlight');
        });
    }
    
    getProcessPath(node) {
        const path = [];
        let current = node;
        
        while (current) {
            const processName = current.querySelector('.process-name')?.textContent || 'Unknown';
            const processPid = current.querySelector('.process-pid')?.textContent.match(/\d+/)?.[0] || '?';
            path.unshift(`${processName} (${processPid})`);
            
            current = current.parentElement?.closest('.tree-node');
        }
        
        return path.join(' → ');
    }
    
    showProcessDetails(node) {
        const processName = node.querySelector('.process-name')?.textContent || 'Unknown';
        const processPid = node.querySelector('.process-pid')?.textContent.match(/\d+/)?.[0] || '?';
        const processPath = this.getProcessPath(node);
        
        // Create a simple details popup
        const detailsHtml = `
            <div class="process-details-popup">
                <h6>Process Details</h6>
                <p><strong>Name:</strong> ${processName}</p>
                <p><strong>PID:</strong> ${processPid}</p>
                <p><strong>Path:</strong> ${processPath}</p>
            </div>
        `;
        
        // You can implement a modal or tooltip here
        console.log('Process details:', detailsHtml);
    }
    
    exportTreeData() {
        if (!this.currentTreeData) return null;
        
        const exportData = {
            timestamp: new Date().toISOString(),
            totalProcesses: this.countTotalProcesses(this.currentTreeData),
            tree: this.currentTreeData
        };
        
        return exportData;
    }
    
    countTotalProcesses(nodes) {
        let count = 0;
        nodes.forEach(node => {
            count++;
            if (node.children && node.children.length > 0) {
                count += this.countTotalProcesses(node.children);
            }
        });
        return count;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Performance optimization: Virtual scrolling for large trees
    setupVirtualScrolling() {
        const container = document.querySelector('#processTree');
        if (!container) return;
        
        let scrollTimeout;
        container.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.updateVisibleNodes();
            }, 100);
        });
    }
    
    updateVisibleNodes() {
        // Implementation for virtual scrolling
        // This would only render visible nodes for performance
    }
}

// Initialize the process tree visualizer
const processTreeVisualizer = new ProcessTreeVisualizer();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProcessTreeVisualizer;
}
