/**
 * Process Monitor System - Main Application
 * Handles navigation, API calls, and data management
 */

class ProcessMonitorApp {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.currentSection = 'dashboard';
        this.refreshInterval = null;
        this.charts = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.loadDashboard();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });
        
        // Process search
        const processSearch = document.getElementById('processSearch');
        if (processSearch) {
            processSearch.addEventListener('input', (e) => {
                this.searchProcesses(e.target.value);
            });
        }
        
        // Top processes buttons
        const topCpuBtn = document.getElementById('topCpuBtn');
        if (topCpuBtn) {
            topCpuBtn.addEventListener('click', () => this.loadTopProcesses('cpu'));
        }
        
        const topMemoryBtn = document.getElementById('topMemoryBtn');
        if (topMemoryBtn) {
            topMemoryBtn.addEventListener('click', () => this.loadTopProcesses('memory'));
        }
        
        // Tree view button
        const treeViewBtn = document.getElementById('treeViewBtn');
        if (treeViewBtn) {
            treeViewBtn.addEventListener('click', () => this.showProcessTree());
        }
        
        // Back to list button
        const backToListBtn = document.getElementById('backToListBtn');
        if (backToListBtn) {
            backToListBtn.addEventListener('click', () => this.showProcessList());
        }
    }
    
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('href').substring(1);
                this.navigateToSection(target);
            });
        });
    }
    
    navigateToSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
        
        // Update navigation active state
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[href="#${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // Load section-specific data
        switch (sectionName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'processes':
                this.loadProcesses();
                break;
            case 'hosts':
                this.loadHosts();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }
    
    async loadDashboard() {
        try {
            this.showLoading(true);
            
            // Load host summary
            const hostsResponse = await this.apiCall('hosts/summary/');
            if (hostsResponse.success) {
                this.renderHostSummaryCards(hostsResponse.data);
            }
            
            // Load latest snapshots
            const snapshotsResponse = await this.apiCall('snapshots/latest/');
            if (snapshotsResponse.success) {
                this.updateSystemOverview(snapshotsResponse.data);
            }
            
            this.updateLastUpdateTime();
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadProcesses() {
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('processes/');
            if (response.success) {
                this.renderProcessTable(response.data.results || response.data);
            }
            
        } catch (error) {
            console.error('Error loading processes:', error);
            this.showError('Failed to load process data');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadHosts() {
        try {
            this.showLoading(true);
            
            const response = await this.apiCall('hosts/');
            if (response.success) {
                this.renderHostCards(response.data.results || response.data);
            }
            
        } catch (error) {
            console.error('Error loading hosts:', error);
            this.showError('Failed to load host data');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadAnalytics() {
        try {
            this.showLoading(true);
            
            // Load process analytics data
            const [hostsResponse, snapshotsResponse, processesResponse] = await Promise.all([
                this.apiCall('hosts/summary/'),
                this.apiCall('snapshots/latest/'),
                this.apiCall('processes/?limit=100')
            ]);
            
            if (hostsResponse.success && snapshotsResponse.success && processesResponse.success) {
                this.renderProcessAnalytics({
                    hosts: hostsResponse.data,
                    snapshots: snapshotsResponse.data,
                    processes: processesResponse.data.results || processesResponse.data
                });
            } else {
                this.showError('Failed to load analytics data');
            }
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics data');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadTopProcesses(type) {
        try {
            this.showLoading(true);
            
            const endpoint = type === 'cpu' ? 'processes/top-cpu/' : 'processes/top-memory/';
            const response = await this.apiCall(endpoint);
            
            if (response.success) {
                this.renderProcessTable(response.data);
            }
            
        } catch (error) {
            console.error(`Error loading top ${type} processes:`, error);
            this.showError(`Failed to load top ${type} processes`);
        } finally {
            this.showLoading(false);
        }
    }
    
    async searchProcesses(query) {
        if (!query.trim()) {
            this.loadProcesses();
            return;
        }
        
        try {
            const response = await this.apiCall(`processes/search/?process_name=${encodeURIComponent(query)}`);
            if (response.success) {
                this.renderProcessTable(response.data);
            }
        } catch (error) {
            console.error('Error searching processes:', error);
        }
    }
    
    async showProcessTree() {
        try {
            this.showLoading(true);
            
            // Get the latest snapshot for tree view
            const response = await this.apiCall('snapshots/latest/');
            if (response.success && response.data.length > 0) {
                const snapshotId = response.data[0].id;
                const treeResponse = await this.apiCall(`snapshots/${snapshotId}/tree/`);
                
                if (treeResponse.success) {
                    // Use the process tree visualizer
                    if (window.processTreeVisualizer) {
                        window.processTreeVisualizer.renderTree(treeResponse.data);
                        this.showSection('processTreeView');
                    } else {
                        this.renderProcessTree(treeResponse.data);
                        this.showSection('processTreeView');
                    }
                }
            }
            
        } catch (error) {
            console.error('Error loading process tree:', error);
            this.showError('Failed to load process tree');
        } finally {
            this.showLoading(false);
        }
    }
    
    showProcessList() {
        this.showSection('processes');
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.style.display = 'block';
        }
    }
    
    renderHostSummaryCards(hosts) {
        const container = document.getElementById('hostSummaryCards');
        if (!container) return;
        
        container.innerHTML = '';
        
        hosts.forEach(host => {
            const card = this.createHostSummaryCard(host);
            container.appendChild(card);
        });
    }
    
    createHostSummaryCard(host) {
        const card = document.createElement('div');
        card.className = 'col-md-4 col-lg-3 mb-3';
        
        const status = this.getHostStatus(host);
        const statusClass = status === 'online' ? 'online' : 'offline';
        
        card.innerHTML = `
            <div class="card host-card cursor-pointer" onclick="app.showHostDetails('${host.id}')">
                <div class="host-status ${statusClass}"></div>
                <div class="card-body">
                    <h6 class="card-title">${host.hostname}</h6>
                    <p class="card-text">
                        <small class="text-muted">
                            <i class="fas fa-desktop me-1"></i>${host.platform || 'Unknown'}
                        </small>
                    </p>
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="metric-value">${host.process_count || 0}</div>
                            <div class="metric-label">Processes</div>
                        </div>
                        <div class="col-6">
                            <div class="metric-value">${host.latest_snapshot?.total_cpu_percent?.toFixed(1) || 0}%</div>
                            <div class="metric-label">CPU</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    renderHostCards(hosts) {
        const container = document.getElementById('hostCards');
        if (!container) return;
        
        container.innerHTML = '';
        
        hosts.forEach(host => {
            const card = this.createHostCard(host);
            container.appendChild(card);
        });
    }
    
    createHostCard(host) {
        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-4 mb-3';
        
        const status = this.getHostStatus(host);
        const statusClass = status === 'online' ? 'online' : 'offline';
        
        card.innerHTML = `
            <div class="card host-card">
                <div class="host-status ${statusClass}"></div>
                <div class="card-body">
                    <h5 class="card-title">${host.hostname}</h5>
                    <p class="card-text">
                        <strong>Platform:</strong> ${host.platform || 'Unknown'}<br>
                        <strong>Architecture:</strong> ${host.architecture || 'Unknown'}<br>
                        <strong>CPU Cores:</strong> ${host.cpu_count || 'Unknown'}<br>
                        <strong>Memory:</strong> ${host.total_memory_gb || 'Unknown'} GB
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            Last seen: ${this.formatDateTime(host.last_seen)}
                        </small>
                        <button class="btn btn-sm btn-outline-primary" onclick="app.showHostDetails('${host.id}')">
                            Details
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    renderProcessTable(processes) {
        const tbody = document.getElementById('processTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        processes.forEach(process => {
            const row = this.createProcessTableRow(process);
            tbody.appendChild(row);
        });
    }
    
    createProcessTableRow(process) {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>
                <div class="process-name">${process.name}</div>
                <small class="text-muted">${process.exe || 'N/A'}</small>
            </td>
            <td><span class="process-pid">${process.pid}</span></td>
            <td><span class="process-pid">${process.ppid || 'N/A'}</span></td>
            <td><span class="process-user">${process.username || 'N/A'}</span></td>
            <td>
                <span class="process-status ${process.status}">${process.status}</span>
            </td>
            <td>
                <span class="cpu-usage">${process.cpu_percent.toFixed(1)}%</span>
            </td>
            <td>
                <span class="memory-usage">${process.memory_rss_mb} MB</span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="app.showProcessDetails('${process.id}')">
                    <i class="fas fa-info-circle"></i>
                </button>
            </td>
        `;
        
        return row;
    }
    
    renderProcessTree(treeData) {
        const container = document.getElementById('processTree');
        if (!container) return;
        
        container.innerHTML = '';
        
        treeData.forEach(node => {
            const treeNode = this.createProcessTreeNode(node);
            container.appendChild(treeNode);
        });
    }
    
    createProcessTreeNode(node) {
        const treeNode = document.createElement('div');
        treeNode.className = 'tree-node';
        
        const hasChildren = node.children && node.children.length > 0;
        const toggleIcon = hasChildren ? 'fas fa-chevron-right' : 'fas fa-circle';
        
        treeNode.innerHTML = `
            <div class="process-info">
                <div class="process-details">
                    <i class="tree-toggle ${hasChildren ? 'cursor-pointer' : ''}" 
                       onclick="${hasChildren ? 'processMonitor.toggleTreeNode(this)' : ''}">
                        <i class="${toggleIcon}"></i>
                    </i>
                    <strong>${node.process.name}</strong>
                    <span class="text-muted">(PID: ${node.process.pid})</span>
                </div>
                <div class="process-metrics">
                    <span class="badge bg-primary">CPU: ${node.process.cpu_percent.toFixed(1)}%</span>
                    <span class="badge bg-info">Memory: ${node.process.memory_rss_mb} MB</span>
                </div>
            </div>
            ${hasChildren ? `<div class="tree-children">${this.renderProcessTreeChildren(node.children)}</div>` : ''}
        `;
        
        return treeNode;
    }
    
    renderProcessTreeChildren(children) {
        return children.map(child => {
            const childNode = this.createProcessTreeNode(child);
            return childNode.outerHTML;
        }).join('');
    }
    
    renderProcessAnalytics(data) {
        const container = document.getElementById('analyticsCharts');
        if (!container) return;
        
        const { hosts, snapshots, processes } = data;
        
        if (!hosts || !snapshots || !processes) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No process data available yet. Run the agent to collect data.
                </div>
            `;
            return;
        }

        // Calculate analytics
        const totalProcesses = processes.length;
        const topCpuProcesses = processes.sort((a, b) => (b.cpu_percent || 0) - (a.cpu_percent || 0)).slice(0, 5);
        const topMemoryProcesses = processes.sort((a, b) => (b.memory_rss || 0) - (a.memory_rss || 0)).slice(0, 5);
        const processStatusCounts = this.getProcessStatusCounts(processes);
        
        // Render process analytics
        container.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-cogs fa-2x mb-2"></i>
                            <h3>${totalProcesses}</h3>
                            <p class="mb-0">Total Processes</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-desktop fa-2x mb-2"></i>
                            <h3>${hosts.length}</h3>
                            <p class="mb-0">Active Hosts</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-camera fa-2x mb-2"></i>
                            <h3>${snapshots.length}</h3>
                            <p class="mb-0">Snapshots</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-play fa-2x mb-2"></i>
                            <h3>${processStatusCounts.running || 0}</h3>
                            <p class="mb-0">Running</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-microchip me-2"></i>Top CPU Processes
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Process</th>
                                            <th>PID</th>
                                            <th>CPU %</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${topCpuProcesses.map(proc => `
                                            <tr>
                                                <td><strong>${proc.name}</strong></td>
                                                <td>${proc.pid}</td>
                                                <td><span class="badge bg-primary">${(proc.cpu_percent || 0).toFixed(1)}%</span></td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-memory me-2"></i>Top Memory Processes
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Process</th>
                                            <th>PID</th>
                                            <th>Memory</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${topMemoryProcesses.map(proc => `
                                            <tr>
                                                <td><strong>${proc.name}</strong></td>
                                                <td>${proc.pid}</td>
                                                <td><span class="badge bg-info">${this.formatBytes(proc.memory_rss || 0)}</span></td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-chart-pie me-2"></i>Process Status Distribution
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${Object.entries(processStatusCounts).map(([status, count]) => `
                                    <div class="col-md-3">
                                        <div class="text-center">
                                            <div class="metric-value">${count}</div>
                                            <div class="metric-label text-capitalize">${status}</div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getLatestMetric(data, field) {
        if (!data || data.length === 0) return 0;
        const latest = data[data.length - 1];
        return latest[field] ? latest[field].toFixed(1) : 0;
    }
    
    getLatestTimestamp(data) {
        if (!data || data.length === 0) return null;
        return data[data.length - 1].timestamp;
    }

    getProcessStatusCounts(processes) {
        const counts = {};
        processes.forEach(proc => {
            const status = proc.status || 'unknown';
            counts[status] = (counts[status] || 0) + 1;
        });
        return counts;
    }

    formatBytes(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    initializeCharts(data) {
        // CPU Frequency Chart
        const cpuCtx = document.getElementById('cpuChart');
        if (cpuCtx) {
            new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: data.map(item => this.formatDateTime(item.timestamp)),
                    datasets: [{
                        label: 'CPU Frequency (MHz)',
                        data: data.map(item => item.cpu_freq_current || 0),
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Frequency (MHz)'
                            }
                        }
                    }
                }
            });
        }
        
        // Memory Chart
        const memoryCtx = document.getElementById('memoryChart');
        if (memoryCtx) {
            new Chart(memoryCtx, {
                type: 'line',
                data: {
                    labels: data.map(item => this.formatDateTime(item.timestamp)),
                    datasets: [{
                        label: 'Memory Usage %',
                        data: data.map(item => item.memory_percent || 0),
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Memory Usage (%)'
                            }
                        }
                    }
                }
            });
        }
    }
    
    toggleTreeNode(toggleElement) {
        const treeNode = toggleElement.closest('.tree-node');
        const children = treeNode.querySelector('.tree-children');
        const icon = toggleElement.querySelector('i');
        
        if (children.classList.contains('collapsed')) {
            children.classList.remove('collapsed');
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-down');
            toggleElement.classList.add('expanded');
        } else {
            children.classList.add('collapsed');
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-right');
            toggleElement.classList.remove('expanded');
        }
    }
    
    updateSystemOverview(snapshots) {
        let totalProcesses = 0;
        let totalCpu = 0;
        let totalMemory = 0;
        
        snapshots.forEach(snapshot => {
            totalProcesses += snapshot.total_processes || 0;
            totalCpu += snapshot.total_cpu_percent || 0;
            totalMemory += snapshot.total_memory_mb || 0;
        });
        
        const totalProcessesElement = document.getElementById('totalProcesses');
        if (totalProcessesElement) {
            totalProcessesElement.textContent = totalProcesses;
        }
        
        const totalHostsElement = document.getElementById('totalHosts');
        if (totalHostsElement) {
            totalHostsElement.textContent = snapshots.length;
        }
    }
    
    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        const lastUpdateElement = document.getElementById('lastUpdate');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = timeString;
        }
        
        const lastUpdateTimeElement = document.getElementById('lastUpdateTime');
        if (lastUpdateTimeElement) {
            lastUpdateTimeElement.textContent = timeString;
        }
    }
    
    getHostStatus(host) {
        const lastSeen = new Date(host.last_seen);
        const now = new Date();
        const diffMinutes = (now - lastSeen) / (1000 * 60);
        
        if (diffMinutes < 5) return 'online';
        if (diffMinutes < 15) return 'warning';
        return 'offline';
    }
    
    formatDateTime(dateString) {
        if (!dateString) return 'Unknown';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMinutes = (now - date) / (1000 * 60);
        
        if (diffMinutes < 1) return 'Just now';
        if (diffMinutes < 60) return `${Math.floor(diffMinutes)}m ago`;
        if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
        return date.toLocaleDateString();
    }
    
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}/${endpoint}`;
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };
        
        try {
            const response = await fetch(url, defaultOptions);
            const data = await response.json();
            
            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.error || 'API request failed' };
            }
        } catch (error) {
            console.error('API call error:', error);
            return { success: false, error: 'Network error' };
        }
    }
    
    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = show ? 'flex' : 'none';
        }
    }
    
    showError(message) {
        // Create and show error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    refreshData() {
        switch (this.currentSection) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'processes':
                this.loadProcesses();
                break;
            case 'hosts':
                this.loadHosts();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 30000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.processMonitor = new ProcessMonitorApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProcessMonitorApp;
}
