/**
 * PipelineUI Class - Rediseñado
 * Manages the UI interactions for the CI/CD pipeline execution view
 */
class PipelineUI {  constructor() {
    this.socket = io();
    this.selectedPipeline = null;
    this.canvas = null;
    this.nodes = [];
    // Timer para duración
    this.startTime = null;
    this.durationTimer = null;
    this.initializeElements();
    this.initializeStepDetailsModal();
    this.setupEventListeners();
    this.setupSocketHandlers();
    this.initializeAutoCenteredCanvas();
    // Initialize UI state
    this.initializeUIState();
    // Check for persistent timer on initialization
    this.checkAndResumePersistentTimer();
  }
  initializeElements() {
    this.elements = {
      startButton: document.getElementById("startButton"),
      statusText: document.getElementById("statusText"),
      statusDetails: document.getElementById("statusDetails"),
      statusIndicator: document.getElementById("statusIndicator"),
      pipelineSelector: document.getElementById("pipelineSelector"),
      projectSelector: document.getElementById("projectSelector"),
      environmentSelector: document.getElementById("environmentSelector"),
      pipelineInfo: document.getElementById("pipelineInfo"),
      pipelineDescription: document.getElementById("pipelineDescription"),
      pipelineDirectory: document.getElementById("pipelineDirectory"),
      pipelineSteps: document.getElementById("pipelineSteps"),
      connectionStatus: document.getElementById("connectionStatus"),
      progressContainer: document.getElementById("progressContainer"),
      progressFill: document.getElementById("progressFill"),
      progressText: document.getElementById("progressText"),
      progressDuration: document.getElementById("progressDuration"),
      currentStepText: document.getElementById("currentStepText"),
      totalRuns: document.getElementById("totalRuns"),
      successRate: document.getElementById("successRate"),
      avgDuration: document.getElementById("avgDuration"),
      refreshBtn: document.getElementById("refreshBtn"),
      stopBtn: document.getElementById("stopButton"),
      pipelineCanvas: document.getElementById("pipelineCanvas"),
      canvasContainer: document.querySelector(".canvas-container"),
      nodesContainer: document.getElementById("nodesContainer"),
      canvasEmptyState: document.getElementById("canvasEmptyState"),
      stepDetailModal: document.getElementById("stepDetailModal"),
      stepDetailModalLabel: document.getElementById("stepDetailModalLabel"),
      stepDetailSubtitle: document.getElementById("stepDetailSubtitle"),
      stepDetailStatus: document.getElementById("stepDetailStatus"),
      stepStartTime: document.getElementById("stepStartTime"),
      stepDuration: document.getElementById("stepDuration"),
      stepLogContent: document.getElementById("stepLogContent"),
      modalStepIcon: document.getElementById("modalStepIcon"),    };
  }

  // ============================================
  // UI STATE INITIALIZATION
  // ============================================

  initializeUIState() {
    // Set initial status
    this.updateStatus("📊 Waiting for project selection", "waiting");
    
    // Ensure start button is disabled initially
    this.disableStartButton();
    
    // Hide pipeline info initially
    this.hidePipelineInfo();
  }

  // ============================================
  // STEP DETAILS MODAL SYSTEM - REBUILT
  // ============================================

  initializeStepDetailsModal() {
    this.stepModal = {
      element: this.elements.stepDetailModal,
      backdrop: null,
      isOpen: false,
      currentStep: null,
    };

    this.setupStepModalEventListeners();
  }
  setupStepModalEventListeners() {
    if (!this.stepModal.element) return;

    // Close button handlers
    const closeButtons = this.stepModal.element.querySelectorAll(
      '[data-bs-dismiss="modal"], .btn-close'
    );
    closeButtons.forEach((button) => {
      button.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.closeStepModal();
      });
    });

    // Prevent modal from closing when clicking inside modal content
    const modalContent = this.stepModal.element.querySelector(".modal-content");
    if (modalContent) {
      modalContent.addEventListener("click", (e) => {
        e.stopPropagation();
      });
    }

    // Modal dialog click to close (clicking outside content)
    const modalDialog = this.stepModal.element.querySelector(".modal-dialog");
    if (modalDialog) {
      modalDialog.addEventListener("click", (e) => {
        if (e.target === modalDialog) {
          this.closeStepModal();
        }
      });
    }

    // Escape key to close
    this.escapeKeyHandler = (e) => {
      if (e.key === "Escape" && this.stepModal.isOpen) {
        e.preventDefault();
        this.closeStepModal();
      }
    };
    document.addEventListener("keydown", this.escapeKeyHandler);
  }
  openStepModal(stepData) {
    if (!this.stepModal.element || this.stepModal.isOpen) return;

    console.log("Opening step modal for:", stepData);

    // Store current step data
    this.stepModal.currentStep = stepData;
    this.stepModal.isOpen = true;

    // Clean any existing modal state first
    this.cleanupModalState();

    // Populate modal content
    this.populateStepModalContent(stepData);

    // Show modal with proper timing and accessibility
    this.stepModal.element.style.display = "block";
    this.stepModal.element.removeAttribute("aria-hidden");
    this.stepModal.element.setAttribute("aria-modal", "true");

    // Force reflow before adding classes
    this.stepModal.element.offsetHeight;

    // Add show class for animation
    this.stepModal.element.classList.add("show");

    // Create backdrop after modal is visible
    setTimeout(() => {
      this.createModalBackdrop();
    }, 10);

    // Set body class for modal
    document.body.classList.add("modal-open");

    // Focus management - delay to avoid conflicts
    setTimeout(() => {
      this.trapFocus();
    }, 150);
  }
  closeStepModal() {
    if (!this.stepModal.element || !this.stepModal.isOpen) return;

    console.log("Closing step modal");

    // Update state first
    this.stepModal.isOpen = false;

    // Remove focus from any modal elements before hiding
    const activeElement = document.activeElement;
    if (this.stepModal.element.contains(activeElement)) {
      activeElement.blur();
    }

    // Hide modal with animation
    this.stepModal.element.classList.remove("show");

    // Wait for animation then fully hide
    setTimeout(() => {
      if (this.stepModal.element) {
        this.stepModal.element.style.display = "none";
        this.stepModal.element.setAttribute("aria-hidden", "true");
        this.stepModal.element.removeAttribute("aria-modal");
      }

      // Clean up state after animation
      this.cleanupModalState();
      this.stepModal.currentStep = null;
    }, 150);
  }
  createModalBackdrop() {
    // Remove existing backdrop
    if (this.stepModal.backdrop) {
      this.stepModal.backdrop.remove();
    }

    // Create new backdrop
    this.stepModal.backdrop = document.createElement("div");
    this.stepModal.backdrop.className = "modal-backdrop fade show";

    // Add backdrop click handler
    this.stepModal.backdrop.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.closeStepModal();
    });

    document.body.appendChild(this.stepModal.backdrop);
  }
  cleanupModalState() {
    // Remove all backdrops
    const backdrops = document.querySelectorAll(".modal-backdrop");
    backdrops.forEach((backdrop) => backdrop.remove());

    if (this.stepModal.backdrop) {
      this.stepModal.backdrop.remove();
      this.stepModal.backdrop = null;
    }

    // Reset body state
    document.body.classList.remove("modal-open");
    document.body.style.overflow = "";
    document.body.style.paddingRight = "";
  }
  // Cleanup method for proper disposal
  destroy() {
    if (this.escapeKeyHandler) {
      document.removeEventListener("keydown", this.escapeKeyHandler);
    }

    if (this.stepModal.isOpen) {
      this.closeStepModal();
    }

    // Stop timer and clear persistent state
    this.stopTimer();

    this.cleanupModalState();
  }

  populateStepModalContent(stepData) {
    if (!stepData) return;

    // Update title and subtitle
    if (this.elements.stepDetailModalLabel) {
      this.elements.stepDetailModalLabel.textContent =
        stepData.name || `Paso ${stepData.index + 1}`;
    }

    if (this.elements.stepDetailSubtitle) {
      this.elements.stepDetailSubtitle.textContent =
        stepData.description || stepData.command || "No description";
    }

    // Update status with proper styling
    if (this.elements.stepDetailStatus) {
      const statusInfo = this.getStepStatusInfo(stepData.status);
      this.elements.stepDetailStatus.innerHTML = `
        <span class="badge ${statusInfo.badgeClass}">
          <i class="${statusInfo.icon} me-1"></i>
          ${statusInfo.text}
        </span>
      `;
    }

    // Update timing information
    if (this.elements.stepStartTime) {
      this.elements.stepStartTime.textContent =
        stepData.startTime ||
        (stepData.start_time
          ? new Date(stepData.start_time).toLocaleString()
          : "-");
    }

    if (this.elements.stepDuration) {
      this.elements.stepDuration.textContent =
        stepData.duration ||
        (stepData.execution_time ? `${stepData.execution_time}s` : "-");
    }

    // Update logs
    if (this.elements.stepLogContent) {
      const logText =
        stepData.logs ||
        stepData.output ||
        stepData.error ||
        "No logs available for this step";
      this.elements.stepLogContent.textContent = logText;

      // Auto-scroll to bottom if logs are long
      setTimeout(() => {
        this.elements.stepLogContent.scrollTop =
          this.elements.stepLogContent.scrollHeight;
      }, 100);
    } // Update modal icon with status-based styling
    if (this.elements.modalStepIcon) {
      const iconElement = this.elements.modalStepIcon.querySelector("i");
      if (iconElement) {
        const statusInfo = this.getStepStatusInfo(stepData.status);
        iconElement.className = statusInfo.icon;

        // Remove existing status classes
        this.elements.modalStepIcon.classList.remove(
          "status-success",
          "status-failure",
          "status-running",
          "status-pending"
        );

        // Add appropriate status class
        const statusClass = `status-${stepData.status || "pending"}`;
        this.elements.modalStepIcon.classList.add(statusClass);
      }
    }
  }
  getStepStatusInfo(status) {
    const statusMap = {
      success: {
        text: "Completed",
        icon: "fas fa-check-circle text-success",
        badgeClass: "bg-success",
      },
      completed: {
        text: "Completed",
        icon: "fas fa-check-circle text-success",
        badgeClass: "bg-success",
      },
      failed: {
        text: "Failed",
        icon: "fas fa-times-circle text-danger",
        badgeClass: "bg-danger",
      },
      error: {
        text: "Error",
        icon: "fas fa-exclamation-triangle text-danger",
        badgeClass: "bg-danger",
      },
      running: {
        text: "Running",
        icon: "fas fa-spinner fa-spin text-primary",
        badgeClass: "bg-primary",
      },
      pending: {
        text: "Pendiente",
        icon: "fas fa-clock text-warning",
        badgeClass: "bg-warning",
      },
      waiting: {
        text: "Waiting",
        icon: "fas fa-hourglass-half text-warning",
        badgeClass: "bg-warning",
      },
      skipped: {
        text: "Skipped",
        icon: "fas fa-forward text-secondary",
        badgeClass: "bg-secondary",
      },
    };

    return (
      statusMap[status] || {
        text: "Desconocido",
        icon: "fas fa-question-circle text-secondary",
        badgeClass: "bg-secondary",
      }
    );
  }

  trapFocus() {
    if (!this.stepModal.element) return;

    const focusableElements = this.stepModal.element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }
  setupEventListeners() {
    // Project selection
    if (this.elements.projectSelector) {
      this.elements.projectSelector.addEventListener("change", (e) => {
        this.handleProjectSelection(e);
      });
    }

    // Environment selection
    if (this.elements.environmentSelector) {
      this.elements.environmentSelector.addEventListener("change", (e) => {
        this.handleEnvironmentSelection(e);
      });
    }

    // Pipeline selection (hidden, for backward compatibility)
    if (this.elements.pipelineSelector) {
      this.elements.pipelineSelector.addEventListener("change", (e) => {
        this.handlePipelineSelection(e);
      });
    }

    // Start button
    if (this.elements.startButton) {
      this.elements.startButton.addEventListener("click", () => {
        this.startPipeline();
      });
    }

    // Control buttons
    if (this.elements.refreshBtn) {
      this.elements.refreshBtn.addEventListener("click", () => {
        this.refreshPipelines();
      });
    }
    if (this.elements.stopBtn) {
      this.elements.stopBtn.addEventListener("click", () => {
        this.stopPipeline();
      });
    }
  }

  setupSocketHandlers() {
    this.socket.on("connect", () => {
      console.log("✅ Connected to server");
      this.updateConnectionStatus(true);
    });

    this.socket.on("disconnect", () => {
      console.log("❌ Disconnected from server");
      this.updateConnectionStatus(false);
    });

    this.socket.on("pipeline_update", (data) => {
      this.updateUI(data);
    });

    this.socket.on("stats_update", (stats) => {
      this.updateStats(stats);
    });
  }

  // ============================================
  // NEW MULTI-ENVIRONMENT SELECTION HANDLERS
  // ============================================

  handleProjectSelection(event) {
    const selectedProject = event.target.value;
    const environmentSelector = this.elements.environmentSelector;
    
    // Clear environment selector
    environmentSelector.innerHTML = '<option value="">Choose deployment type...</option>';
    environmentSelector.disabled = true;
    
    // Reset pipeline selection
    this.selectedPipeline = null;
    this.hidePipelineInfo();
    this.disableStartButton();
    
    if (selectedProject && window.pipelineData && window.pipelineData.grouped[selectedProject]) {
      const projectData = window.pipelineData.grouped[selectedProject];
      const environments = projectData.environments;
      
      // Add environment options with descriptions
      Object.keys(environments).forEach(envKey => {
        const env = environments[envKey];
        const option = document.createElement('option');
        option.value = envKey;
        option.setAttribute('data-path', env.path);
        option.setAttribute('data-description', env.description);
        option.setAttribute('data-directory', env.directory);
        option.setAttribute('data-steps', env.steps_count);
        
        // Create descriptive text based on environment
        let envTitle = '';
        let envDescription = '';
        
        switch(envKey) {
          case 'development':
          case 'dev':
            envTitle = '🚀 Development (Persistent)';
            envDescription = 'Keeps services running for active development';
            break;
          case 'test':
          case 'testing':
            envTitle = '🧪 Testing (E2E with Cleanup)';
            envDescription = 'Full testing cycle with automatic cleanup';
            break;
          case 'prod':
          case 'production':
            envTitle = '📊 Production (Monitoring)';
            envDescription = 'Production deployment with monitoring';
            break;
          default:
            envTitle = `📋 ${envKey.charAt(0).toUpperCase() + envKey.slice(1)}`;
            envDescription = env.description || 'Custom pipeline configuration';
        }
        
        option.textContent = envTitle;
        option.setAttribute('data-env-description', envDescription);
        environmentSelector.appendChild(option);
      });
      
      environmentSelector.disabled = false;
      this.updateStatus(`📁 Project "${selectedProject}" selected - Choose deployment type`, "waiting");
    } else {
      this.updateStatus("📊 Waiting for project selection", "waiting");
    }
  }

  handleEnvironmentSelection(event) {
    const selectedOption = event.target.selectedOptions[0];
    
    if (selectedOption && selectedOption.value) {
      const pipelinePath = selectedOption.getAttribute('data-path');
      const description = selectedOption.getAttribute('data-description');
      const envDescription = selectedOption.getAttribute('data-env-description');
      const directory = selectedOption.getAttribute('data-directory');
      const steps = selectedOption.getAttribute('data-steps');
      
      // Set the selected pipeline
      this.selectedPipeline = pipelinePath;
      
      // Update the hidden pipeline selector for backward compatibility
      if (this.elements.pipelineSelector) {
        this.elements.pipelineSelector.value = pipelinePath;
      }
      
      // Update pipeline info
      if (this.elements.pipelineDescription) {
        this.elements.pipelineDescription.textContent = envDescription || description;
      }
      if (this.elements.pipelineDirectory) {
        this.elements.pipelineDirectory.textContent = directory;
      }
      if (this.elements.pipelineSteps) {
        this.elements.pipelineSteps.textContent = steps + " steps";
      }
      
      this.showPipelineInfo();
      this.enableStartButton();
      
      this.updateStatus(`✅ ${selectedOption.textContent} selected - Ready to execute`, "ready");
    } else {
      this.selectedPipeline = null;
      this.hidePipelineInfo();
      this.disableStartButton();
      this.updateStatus("🔧 Waiting for deployment type selection", "waiting");
    }
  }

  // ============================================
  // HELPER METHODS FOR UI STATE MANAGEMENT
  // ============================================

  showPipelineInfo() {
    if (this.elements.pipelineInfo) {
      this.elements.pipelineInfo.style.display = "block";
    }
  }

  hidePipelineInfo() {
    if (this.elements.pipelineInfo) {
      this.elements.pipelineInfo.style.display = "none";
    }
  }

  enableStartButton() {
    if (this.elements.startButton) {
      this.elements.startButton.disabled = false;
    }
  }

  disableStartButton() {
    if (this.elements.startButton) {
      this.elements.startButton.disabled = true;
    }
  }

  // ============================================
  // LEGACY PIPELINE SELECTION HANDLER
  // ============================================

  handlePipelineSelection(event) {
    const selectedOption = event.target.selectedOptions[0];
    if (selectedOption && selectedOption.value) {
      this.selectedPipeline = selectedOption.value;
      const description = selectedOption.getAttribute("data-description");
      const directory = selectedOption.getAttribute("data-directory");
      const steps = selectedOption.getAttribute("data-steps");

      if (this.elements.pipelineDescription) {
        this.elements.pipelineDescription.textContent = description;
      }
      if (this.elements.pipelineDirectory) {
        this.elements.pipelineDirectory.textContent = directory;
      }
      if (this.elements.pipelineSteps) {
        this.elements.pipelineSteps.textContent = steps + " steps";
      }
      if (this.elements.pipelineInfo) {
        this.elements.pipelineInfo.style.display = "block";
      }

      if (this.elements.startButton) {
        this.elements.startButton.disabled = false;
      }
      this.updateStatus(
        "✅ Pipeline selected - " + selectedOption.text,
        "ready"
      );
    } else {
      this.selectedPipeline = null;
      if (this.elements.pipelineInfo) {
        this.elements.pipelineInfo.style.display = "none";
      }
      if (this.elements.startButton) {
        this.elements.startButton.disabled = true;
      }
      this.updateStatus("📊 Waiting for pipeline selection", "waiting");
    }
  }
  startPipeline() {
    if (!this.selectedPipeline) {
      this.showNotification(
        "⚠️ Please select a pipeline before executing",
        "warning"
      );
      return;
    }

    console.log("🚀 Starting pipeline:", this.selectedPipeline);

    // Start the timer
    this.startTimer();

    this.socket.emit("start_pipeline", {
      pipeline_file: this.selectedPipeline,
    });
    this.updateStatus("🚀 Starting pipeline...", "starting");

    if (this.elements.startButton) {
      this.elements.startButton.disabled = true;
    }
    if (this.elements.pipelineSelector) {
      this.elements.pipelineSelector.disabled = true;
    }
    if (this.elements.stopBtn) {
      this.elements.stopBtn.style.display = "block";
    }
  }
  stopPipeline() {
    this.socket.emit("stop_pipeline", {});
    this.showNotification("⏹️ Stop request sent", "info");

    // Stop the timer when pipeline is stopped and clear persistent state
    this.stopTimer();
  }
  // Timer Management Methods
  checkAndResumePersistentTimer() {
    try {
      const persistentTimer = localStorage.getItem("pipelineTimer");
      if (persistentTimer) {
        const timerData = JSON.parse(persistentTimer);
        const { startTime, selectedPipeline } = timerData;

        // Check if the stored timer is still valid (not too old, e.g., within 24 hours)
        const maxAge = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
        const elapsed = Date.now() - startTime;

        if (elapsed < maxAge && startTime && selectedPipeline) {
          console.log("🔄 Resuming persistent timer from localStorage");
          this.startTime = startTime;
          this.selectedPipeline = selectedPipeline;

          // Start the display timer immediately
          this.updateTimerDisplay();
          this.durationTimer = setInterval(() => {
            this.updateTimerDisplay();
          }, 1000);

          // Update UI to reflect the selected pipeline
          if (this.elements.pipelineSelector) {
            this.elements.pipelineSelector.value = selectedPipeline;
            // Trigger change event to update UI
            const event = new Event("change");
            this.elements.pipelineSelector.dispatchEvent(event);
          }
        } else {
          // Clear expired timer data
          localStorage.removeItem("pipelineTimer");
        }
      }
    } catch (error) {
      console.warn("⚠️ Error resuming persistent timer:", error);
      localStorage.removeItem("pipelineTimer");
    }
  }

  startTimer() {
    if (this.durationTimer) {
      clearInterval(this.durationTimer);
    }

    this.startTime = Date.now();
    this.updateTimerDisplay();

    // Store timer state in localStorage for persistence
    try {
      const timerData = {
        startTime: this.startTime,
        selectedPipeline: this.selectedPipeline,
      };
      localStorage.setItem("pipelineTimer", JSON.stringify(timerData));
      console.log("💾 Timer state saved to localStorage");
    } catch (error) {
      console.warn("⚠️ Failed to save timer state to localStorage:", error);
    }

    this.durationTimer = setInterval(() => {
      this.updateTimerDisplay();
    }, 1000); // Update every second
  }

  stopTimer() {
    if (this.durationTimer) {
      clearInterval(this.durationTimer);
      this.durationTimer = null;
    }

    // Clear persistent timer state
    try {
      localStorage.removeItem("pipelineTimer");
      console.log("🗑️ Timer state cleared from localStorage");
    } catch (error) {
      console.warn("⚠️ Failed to clear timer state from localStorage:", error);
    }
  }

  updateTimerDisplay() {
    if (!this.startTime || !this.elements.progressDuration) {
      return;
    }

    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    const formattedTime = `${minutes.toString().padStart(2, "0")}:${seconds
      .toString()
      .padStart(2, "0")}`;
    this.elements.progressDuration.textContent = formattedTime;
  }
  resetTimer() {
    this.stopTimer();
    this.startTime = null;
    if (this.elements.progressDuration) {
      this.elements.progressDuration.textContent = "00:00";
    }

    // Clear persistent timer state
    try {
      localStorage.removeItem("pipelineTimer");
      console.log("🔄 Timer reset and localStorage cleared");
    } catch (error) {
      console.warn("⚠️ Failed to clear timer state during reset:", error);
    }
  }

  // Canvas Functionality
  initializeAutoCenteredCanvas() {
    if (!this.elements.canvasContainer) return;

    this.canvas = this.elements.canvasContainer;
    // Remove any existing transform
    if (this.elements.nodesContainer) {
      this.elements.nodesContainer.style.transform = "";
    }
  }
  autoScaleCanvas() {
    if (!this.elements.nodesContainer || this.nodes.length === 0) return;

    const containerRect = this.elements.canvasContainer.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const containerHeight = containerRect.height;

    // Calculate total width needed for all nodes with improved spacing
    const nodeWidth = 120;
    const nodeSpacing = 20;
    const totalNodesWidth =
      this.nodes.length * nodeWidth + (this.nodes.length - 1) * nodeSpacing;
    const horizontalPadding = 80; // Increased padding for better margins
    const verticalPadding = 60; // Increased padding top and bottom

    // Calculate scale to fit all nodes with better margins
    const scaleX = (containerWidth - horizontalPadding) / totalNodesWidth;
    const scaleY = (containerHeight - verticalPadding) / 140; // 140 is node height
    const scale = Math.min(scaleX, scaleY, 1); // Don't scale up, only down if needed

    // Apply scale with smooth transition
    if (scale < 1) {
      this.elements.nodesContainer.style.transform = `scale(${scale})`;
      this.elements.nodesContainer.style.transformOrigin = "center center";
    } else {
      this.elements.nodesContainer.style.transform = "";
    }

    // Add a subtle indication when scaled
    if (scale < 0.8) {
      this.elements.nodesContainer.style.filter =
        "drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))";
    } else {
      this.elements.nodesContainer.style.filter = "";
    }

    // Add subtle scaling animation for small screens
    if (scale < 0.9) {
      this.elements.nodesContainer.style.transition =
        "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)";
    }
  }

  clearNodes() {
    if (this.elements.nodesContainer) {
      this.elements.nodesContainer.innerHTML = "";
      // Reset any transform when clearing
      this.elements.nodesContainer.style.transform = "";
    }
    this.nodes = [];

    if (this.elements.canvasEmptyState) {
      this.elements.canvasEmptyState.style.display = "flex";
    }
  }
  createPipelineNode(step, index, total) {
    const node = document.createElement("div");
    node.className = "pipeline-node";
    node.dataset.stepIndex = index;

    // Centered layout: newest nodes appear in center, older ones shift left
    const containerRect = this.elements.canvasContainer.getBoundingClientRect();
    const containerCenterX = containerRect.width / 2;
    const containerCenterY = containerRect.height / 2;

    const nodeWidth = 120;
    const nodeSpacing = 20; // Reduced spacing for better fit

    // Calculate positions so nodes are centered horizontally
    const totalWidth = total * nodeWidth + (total - 1) * nodeSpacing;
    const startX = containerCenterX - totalWidth / 2;

    const posX = startX + index * (nodeWidth + nodeSpacing);
    const posY = containerCenterY - 70; // Center vertically (70 is half node height)

    node.style.left = posX + "px";
    node.style.top = posY + "px";

    // Enhanced node content with better styling
    node.innerHTML = `
            <div class="node-circle ${step.status || "pending"}">
                <i class="fas fa-${this.getStepNodeIcon(step.status)}"></i>
            </div>
            <div class="node-label">${step.name}</div>
            <div class="node-status ${
              step.status || "pending"
            }">${this.getStatusText(step.status)}</div>
            <div class="node-index">${index + 1}</div>
        `;

    // Add click handler to show step details
    node.addEventListener("click", () => {
      this.showStepDetail(step, index);
    });

    // Add connection line if not the last node
    if (index < total - 1) {
      const line = document.createElement("div");
      line.className = `connection-line ${
        step.status === "success" ? "completed" : ""
      }`;
      line.style.position = "absolute";
      line.style.left = posX + nodeWidth + "px";
      line.style.top = posY + 40 + "px"; // Center of the node circle
      line.style.width = nodeSpacing + "px";
      line.style.height = "4px";
      line.style.background =
        step.status === "success"
          ? "linear-gradient(90deg, var(--success) 0%, var(--primary) 100%)"
          : "linear-gradient(90deg, var(--gray-300) 0%, var(--gray-400) 100%)";
      line.style.borderRadius = "2px";
      line.style.transition = "all 0.3s ease";
      line.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.1)";
      this.elements.nodesContainer.appendChild(line);
    }

    this.elements.nodesContainer.appendChild(node);
    this.nodes.push(node);

    // Enhanced auto-scale canvas after adding node
    setTimeout(() => this.autoScaleCanvas(), 50);

    return node;
  }
  getStepNodeIcon(status) {
    const icons = {
      running: "spinner fa-spin",
      success: "check",
      failure: "times",
      pending: "clock",
    };
    return icons[status] || "circle";
  }
  showStepDetail(step, index) {
    // Prepare comprehensive step data for the modal
    const stepData = {
      name: step.name || `Paso ${index + 1}`,
      description:
        step.description || step.command || `Executing step ${index + 1}`,
      status: step.status || "pending",
      startTime: step.start_time,
      duration: step.duration,
      execution_time: step.execution_time,
      logs: step.output || step.error || step.logs,
      output: step.output,
      error: step.error,
      command: step.command,
      index: index,
    };

    console.log("Showing step detail for:", stepData);

    // Open modal with step data using new system
    this.openStepModal(stepData);
  }

  getStatusBadgeClass(status) {
    const classes = {
      running: "primary",
      success: "success",
      failure: "danger",
      pending: "secondary",
    };
    return classes[status] || "secondary";
  }

  updateSteps(steps) {
    if (!this.elements.nodesContainer) return;

    // Clear existing nodes
    this.clearNodes();

    if (steps.length === 0) {
      if (this.elements.canvasEmptyState) {
        this.elements.canvasEmptyState.style.display = "flex";
      }
      return;
    } // Hide empty state
    if (this.elements.canvasEmptyState) {
      this.elements.canvasEmptyState.style.display = "none";
    }

    // Create nodes for each step
    steps.forEach((stepData, index) => {
      this.createPipelineNode(stepData, index, steps.length);
    });

    // Auto-scale the view after creating nodes
    setTimeout(() => {
      this.autoScaleCanvas();
    }, 100);
  }

  refreshPipelines() {
    if (this.elements.refreshBtn) {
      this.elements.refreshBtn.innerHTML =
        '<i class="fas fa-sync-alt fa-spin"></i>';
    }
    setTimeout(() => {
      location.reload();
    }, 500);
  }

  updateConnectionStatus(connected) {
    if (this.elements.connectionStatus) {
      this.elements.connectionStatus.className = `connection-status ${
        connected ? "connected" : "disconnected"
      }`;
      this.elements.connectionStatus.innerHTML = connected
        ? '<i class="fas fa-wifi"></i> Connected'
        : '<i class="fas fa-wifi"></i> Disconnected';
    }
  }

  updateStatus(text, type = "default", details = "") {
    if (this.elements.statusText) {
      this.elements.statusText.textContent = text;
    }
    if (this.elements.statusDetails) {
      this.elements.statusDetails.textContent = details;
    }

    if (this.elements.statusIndicator) {
      this.elements.statusIndicator.className = "status-indicator";
      if (type !== "default") {
        this.elements.statusIndicator.classList.add(type);
      }
    }
  }

  updateProgress(progress, currentStep = "") {
    if (progress !== undefined && this.elements.progressFill) {
      this.elements.progressFill.style.width = progress + "%";
    }
    if (progress !== undefined && this.elements.progressText) {
      this.elements.progressText.textContent = Math.round(progress) + "%";
    }

    if (currentStep && this.elements.currentStepText) {
      this.elements.currentStepText.textContent = `Executing: ${currentStep}`;
    }
  }

  updateStats(stats) {
    if (this.elements.totalRuns) {
      this.elements.totalRuns.textContent = stats.total_runs || 0;
    }
    if (this.elements.successRate) {
      this.elements.successRate.textContent = (stats.success_rate || 0) + "%";
    }
    if (this.elements.avgDuration) {
      this.elements.avgDuration.textContent = (stats.avg_duration || 0) + "s";
    }
  }
  updateUI(data) {
    // Update overall status
    if (data.running) {
      // Start timer if not already started (pipeline just started or resuming)
      if (!this.durationTimer && !this.startTime) {
        // Check if we have persistent timer data to resume
        try {
          const persistentTimer = localStorage.getItem("pipelineTimer");
          if (persistentTimer) {
            const timerData = JSON.parse(persistentTimer);
            if (timerData.startTime) {
              console.log("🔄 Resuming timer from localStorage in updateUI");
              this.startTime = timerData.startTime;
              this.selectedPipeline =
                timerData.selectedPipeline || data.pipeline_file;

              // Start the display timer
              this.updateTimerDisplay();
              this.durationTimer = setInterval(() => {
                this.updateTimerDisplay();
              }, 1000);
            } else {
              // No valid timer data, start fresh
              this.startTimer();
            }
          } else {
            // No persistent data, start fresh
            this.startTimer();
          }
        } catch (error) {
          console.warn("⚠️ Error resuming timer in updateUI:", error);
          this.startTimer();
        }
      }

      this.updateStatus(
        "⚡ Running pipeline...",
        "running",
        `Pipeline: ${data.pipeline_file || "Desconocido"}`
      );

      if (this.elements.startButton) {
        this.elements.startButton.disabled = true;
      }
      if (this.elements.pipelineSelector) {
        this.elements.pipelineSelector.disabled = true;
      }
      if (this.elements.progressContainer) {
        this.elements.progressContainer.style.display = "block";
      }
      if (this.elements.stopBtn) {
        this.elements.stopBtn.style.display = "block";
      }

      if (data.progress !== undefined) {
        this.updateProgress(data.progress, data.current_step);
      }
    } else {
      // Pipeline is not running, stop the timer
      this.stopTimer();

      const lastLog =
        data.log && data.log.length > 0 ? data.log[data.log.length - 1] : "";
      if (lastLog.includes("Completed successfully")) {
        this.updateStatus(
          "✅ Completed successfully",
          "success",
          `Duration: ${data.duration || "N/A"}`
        );
      } else if (
        lastLog.includes("Finished with errors") ||
        lastLog.includes("Critical error")
      ) {
        this.updateStatus(
          "❌ Finished with errors",
          "error",
          `Duration: ${data.duration || "N/A"}`
        );
      } else if (this.selectedPipeline) {
        this.updateStatus("⏹️ Ready to execute", "ready");
      } else {
        this.updateStatus("📊 Waiting for pipeline selection", "waiting");
      }

      if (this.elements.startButton) {
        this.elements.startButton.disabled = !this.selectedPipeline;
      }
      if (this.elements.pipelineSelector) {
        this.elements.pipelineSelector.disabled = false;
      }
      if (this.elements.progressContainer) {
        this.elements.progressContainer.style.display = "none";
      }
      if (this.elements.stopBtn) {
        this.elements.stopBtn.style.display = "none";
      }
    }

    // Update steps if included in the update
    if (data.steps !== undefined) {
      this.updateSteps(data.steps);
    }
  }

  getStepIcon(status) {
    const icons = {
      running: "spinner fa-spin",
      success: "check-circle",
      failure: "times-circle",
      pending: "clock",
    };
    return icons[status] || "circle";
  }
  getStatusText(status) {
    const texts = {
      running: "Running",
      success: "Completed",
      failure: "Failed",
      pending: "Pending",
    };
    return texts[status] || "Unknown";
  }

  showNotification(message, type = "info") {
    // Simple notification system
    const notification = document.createElement("div");
    notification.className = `alert alert-${
      type === "warning" ? "warning" : type === "error" ? "danger" : "info"
    } alert-dismissible fade show`;
    notification.style.cssText =
      "position: fixed; top: 80px; right: 20px; z-index: 1050; min-width: 300px;";
    notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
    document.body.appendChild(notification);

    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5001);
  }

  refreshStats() {
    fetch("/api/stats")
      .then((response) => response.json())
      .then((stats) => this.updateStats(stats))
      .catch((error) => console.error("Error loading stats:", error));
  }
  // Emergency cleanup method - can be called manually if needed
  forceCleanupAllModals() {
    // Remove all modal backdrops
    const allBackdrops = document.querySelectorAll(".modal-backdrop");
    allBackdrops.forEach((backdrop) => {
      backdrop.remove();
    });

    // Reset all modals to hidden state
    const allModals = document.querySelectorAll(".modal");
    allModals.forEach((modal) => {
      modal.classList.remove("show");
      modal.style.display = "none";
      modal.setAttribute("aria-hidden", "true");
      modal.removeAttribute("aria-modal");
      modal.removeAttribute("role");
    });

    // Reset body state
    document.body.classList.remove("modal-open");
    document.body.style.overflow = "";
    document.body.style.paddingRight = "";

    // Also cleanup timer state as part of emergency cleanup
    try {
      localStorage.removeItem("pipelineTimer");
      console.log("🧹 Timer state also cleared during emergency cleanup");
    } catch (error) {
      console.warn(
        "⚠️ Failed to clear timer state during emergency cleanup:",
        error
      );
    }

    console.log("🧹 Emergency modal cleanup completed");
  }
}

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  // Clean up any stuck modal state before creating new instance
  const existingBackdrops = document.querySelectorAll(".modal-backdrop");
  existingBackdrops.forEach((backdrop) => backdrop.remove());

  document.body.classList.remove("modal-open");
  document.body.style.overflow = "";
  document.body.style.paddingRight = "";

  // Create new instance
  window.pipelineUI = new PipelineUI();

  // Expose emergency cleanup globally for debugging
  window.forceCleanupModals = () => {
    if (window.pipelineUI) {
      window.pipelineUI.forceCleanupAllModals();
    }
  };
});
