// Projects UI Management
class ProjectsUI {
  constructor() {
    this.socket = io();
    this.currentStep = 1;
    this.selectedProjectType = null;
    this.projectTypes = [];
    this.flaskMode = "standard";
    this.djangoMode = "standard";
    this.reactLanguage = "javascript";
    this.reactPort = 3000;
    this.cookiecutterConfigs = {}; // Changed: object to store configs by type
    this.initializeEventListeners();
    this.initializeSocket();
    this.loadProjectTypes();
    this.updateConnectionStatus();
    this.initializeModeStates();
    this.startStatsTimer();
  }

  initializeEventListeners() {
    // Wizard navigation
    document
      .getElementById("nextStepBtn")
      .addEventListener("click", () => this.nextStep());
    document
      .getElementById("prevStepBtn")
      .addEventListener("click", () => this.prevStep());
    document
      .getElementById("createProjectBtn")
      .addEventListener("click", () => this.createProject());

    // Form inputs
    document
      .getElementById("projectName")
      .addEventListener("input", () => this.validateForm());
    document
      .getElementById("outputDir")
      .addEventListener("input", () => this.validateForm());

    // Flask mode selector
    document.addEventListener("change", (e) => {
      if (e.target.name === "flaskMode") {
        this.flaskMode = e.target.value;
        this.handleFlaskModeChange();
      } else if (e.target.name === "djangoMode") {
        this.djangoMode = e.target.value;
        this.handleDjangoModeChange();
      } else if (e.target.name === "reactLanguage") {
        this.reactLanguage = e.target.value;
        this.handleReactLanguageChange();
      }
    });

    // React port input
    document.addEventListener("input", (e) => {
      if (e.target.id === "reactPort") {
        this.reactPort = parseInt(e.target.value) || 3000;
        this.validateForm();
      }
    });
  }
  initializeSocket() {
    this.socket.on("connect", () => {
      console.log("Connected to server");
      this.updateConnectionStatus(true);
      // Update stats when connected
      this.updateStats();
    });

    this.socket.on("disconnect", () => {
      console.log("Disconnected from server");
      this.updateConnectionStatus(false);
    });

    this.socket.on("project_creation_update", (data) => {
      this.handleProjectCreationUpdate(data);
    });

    // Handle both project types events for compatibility
    this.socket.on("project_types_update", (data) => {
      this.handleProjectTypesResponse(data);
    });

    this.socket.on("project_types", (data) => {
      this.handleProjectTypesResponse(data);
    });

    this.socket.on("cookiecutter_config_response", (data) => {
      this.handleCookiecutterConfigResponse(data);
    });
  }

  updateConnectionStatus(connected = false) {
    const statusElement = document.getElementById("connectionStatus");
    if (connected) {
      statusElement.innerHTML =
        '<i class="fas fa-wifi text-success"></i> <span>Connected</span>';
      statusElement.className = "connection-status connected";
    } else {
      statusElement.innerHTML =
        '<i class="fas fa-wifi text-warning"></i> <span>Connecting...</span>';
      statusElement.className = "connection-status connecting";
    }
  }

  loadProjectTypes() {
    console.log("🔄 Requesting project types...");
    this.socket.emit("get_project_types");
  }

  handleProjectTypesResponse(data) {
    console.log("📋 Project types response:", data);
    if (data.error) {
      console.error("❌ Error loading types:", data.error);
      this.showError("Error loading project types: " + data.error);
      return;
    }

    this.projectTypes = data.types || [];
    console.log("📁 Types loaded:", this.projectTypes.length);
    this.renderProjectTypes();
    this.updateStats();
  }

  renderProjectTypes() {
    const container = document.getElementById("projectTypesContainer");
    container.innerHTML = "";

    if (this.projectTypes.length === 0) {
      container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>                        <h5>No project types available</h5>
                        <p class="text-muted">Please check the server configuration.</p>
                        <button class="btn btn-primary" onclick="window.location.reload()">
                            <i class="fas fa-sync-alt me-2"></i>Reload
                        </button>
                    </div>
                </div>
            `;
      return;
    }

    this.projectTypes.forEach((type) => {
      const typeCard = this.createProjectTypeCard(type);
      container.appendChild(typeCard);
    });
  }

  createProjectTypeCard(type) {
    const col = document.createElement("div");
    col.className = "col-md-4 col-lg-3";

    const iconClass = this.getProjectTypeIcon(type.name);

    col.innerHTML = `
            <div class="project-type-card" data-type="${type.name}">
                <div class="project-type-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="project-type-name">${type.display_name}</div>
                <div class="project-type-description">${type.description}</div>
            </div>
        `;

    col.querySelector(".project-type-card").addEventListener("click", () => {
      this.selectProjectType(type);
    });

    return col;
  }

  getProjectTypeIcon(typeName) {
    const icons = {
      flask: "fab fa-python",
      django: "fab fa-python",
      node: "fab fa-node-js",
      nodejs: "fab fa-node-js",
      express: "fab fa-node-js",
      react: "fab fa-react",
      vue: "fab fa-vuejs",
      angular: "fab fa-angular",
    };
    return icons[typeName] || "fas fa-cube";
  }

  showError(message) {
    const container = document.getElementById("projectTypesContainer");
    container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${message}
                </div>
            </div>
        `;
  }

  selectProjectType(type) {
    // Remove previous selection
    document.querySelectorAll(".project-type-card").forEach((card) => {
      card.classList.remove("selected");
    });

    // Select new card
    const selectedCard = document.querySelector(`[data-type="${type.name}"]`);
    selectedCard.classList.add("selected");

    this.selectedProjectType = type;

    // Clear cookiecutter form when changing project type
    this.clearCookiecutterForm();

    // Show Flask mode selector if Flask is selected
    const flaskModeSelector = document.getElementById("flaskModeSelector");
    // Show Django mode selector if Django is selected
    const djangoModeSelector = document.getElementById("djangoModeSelector");
    // Show React mode selector if React is selected
    const reactModeSelector = document.getElementById("reactModeSelector");

    if (type.name === "flask") {
      flaskModeSelector.style.display = "block";
      if (djangoModeSelector) djangoModeSelector.style.display = "none";
      if (reactModeSelector) reactModeSelector.style.display = "none";
      // Reset Django mode and sync Flask mode
      this.djangoMode = "standard";
      console.log(`🔧 Switching to Flask, mode: ${this.flaskMode}`);
      this.syncModeButtons("flask");
      this.updateConfigForCurrentMode();
    } else if (type.name === "django") {
      if (djangoModeSelector) djangoModeSelector.style.display = "block";
      flaskModeSelector.style.display = "none";
      if (reactModeSelector) reactModeSelector.style.display = "none";
      // Reset Flask mode and sync Django mode
      this.flaskMode = "standard";
      console.log(`🔧 Switching to Django, mode: ${this.djangoMode}`);
      this.syncModeButtons("django");
      this.updateConfigForCurrentMode();
    } else if (type.name === "react") {
      reactModeSelector.style.display = "block";
      if (flaskModeSelector) flaskModeSelector.style.display = "none";
      if (djangoModeSelector) djangoModeSelector.style.display = "none";
      // Reset other modes
      this.flaskMode = "standard";
      this.djangoMode = "standard";
      this.syncModeButtons("flask");
      this.syncModeButtons("django");
      console.log(`🔧 Switching to ${type.name}, using React config`);
      this.showStandardConfig();
    } else {
      flaskModeSelector.style.display = "none";
      if (djangoModeSelector) djangoModeSelector.style.display = "none";
      if (reactModeSelector) reactModeSelector.style.display = "none";
      this.flaskMode = "standard";
      this.djangoMode = "standard";
      console.log(`🔧 Switching to ${type.name}, using standard config`);
      this.showStandardConfig();
    }

    this.validateForm();
  }

  getCurrentCookiecutterConfig() {
    if (!this.selectedProjectType) return null;
    return this.cookiecutterConfigs[this.selectedProjectType.name] || null;
  }

  setCurrentCookiecutterConfig(config) {
    if (!this.selectedProjectType) return;
    this.cookiecutterConfigs[this.selectedProjectType.name] = config;
  }

  clearCookiecutterForm() {
    const formContainer = document.getElementById("cookiecutterForm");
    if (formContainer) {
      formContainer.innerHTML = "";
    }
  }

  /**
   * Syncs mode buttons according to the current project type
   * @param {string} projectType - Project type ('flask' or 'django')
   */
  syncModeButtons(projectType) {
    if (projectType === "flask") {
      // Sync Flask buttons
      const flaskStandardBtn = document.getElementById("flaskModeStandard");
      const flaskCustomBtn = document.getElementById("flaskModeCustom");

      if (flaskStandardBtn && flaskCustomBtn) {
        if (this.flaskMode === "standard") {
          flaskStandardBtn.checked = true;
          flaskCustomBtn.checked = false;
        } else {
          flaskStandardBtn.checked = false;
          flaskCustomBtn.checked = true;
        }
      }
    } else if (projectType === "django") {
      // Sync Django buttons
      const djangoStandardBtn = document.getElementById("djangoModeStandard");
      const djangoCustomBtn = document.getElementById("djangoModeCustom");

      if (djangoStandardBtn && djangoCustomBtn) {
        if (this.djangoMode === "standard") {
          djangoStandardBtn.checked = true;
          djangoCustomBtn.checked = false;
        } else {
          djangoStandardBtn.checked = false;
          djangoCustomBtn.checked = true;
        }
      }
    }
  }

  /**
   * Updates the config and shows the appropriate form according to the current mode
   */
  updateConfigForCurrentMode() {
    if (!this.selectedProjectType) return;

    const projectType = this.selectedProjectType.name;
    let currentMode = "standard";

    if (projectType === "flask") {
      currentMode = this.flaskMode;
    } else if (projectType === "django") {
      currentMode = this.djangoMode;
    }

    // Show appropriate config
    if (currentMode === "standard") {
      this.showStandardConfig();
    } else if (currentMode === "custom") {
      // Only load config if not already loaded for this project
      const currentConfig = this.getCurrentCookiecutterConfig();
      if (!currentConfig) {
        this.showAdvancedConfig(); // This will load the config automatically
      } else {
        // If we already have the config, show the form directly
        document.getElementById("standardConfig").style.display = "none";
        document.getElementById("advancedConfig").style.display = "block";
        this.renderCookiecutterForm();
      }
    }
  }

  /**
   * Initializes the mode button states when the page loads
   */
  initializeModeStates() {
    // Make sure standard buttons are selected by default
    const flaskStandardBtn = document.getElementById("flaskModeStandard");
    const djangoStandardBtn = document.getElementById("djangoModeStandard");

    if (flaskStandardBtn) {
      flaskStandardBtn.checked = true;
    }

    if (djangoStandardBtn) {
      djangoStandardBtn.checked = true;
    }

    // Make sure standard config is visible by default
    this.showStandardConfig();
  }

  nextStep() {
    if (this.currentStep === 1 && this.selectedProjectType) {
      this.currentStep = 2;
      this.showStep(2);
      this.updatePreview();
    }
  }

  prevStep() {
    if (this.currentStep === 2) {
      this.currentStep = 1;
      this.showStep(1);
    }
  }

  showStep(step) {
    // Hide all steps
    document.querySelectorAll(".wizard-step").forEach((stepEl) => {
      stepEl.classList.remove("active");
    });

    // Show current step
    document.getElementById(`step${step}`).classList.add("active");

    // Update controls
    const prevBtn = document.getElementById("prevStepBtn");
    const nextBtn = document.getElementById("nextStepBtn");
    const createBtn = document.getElementById("createProjectBtn");

    if (step === 1) {
      prevBtn.style.display = "none";
      nextBtn.style.display = "inline-block";
      createBtn.style.display = "none";

      // When returning to step 1, sync mode buttons if a project is selected
      if (this.selectedProjectType) {
        const projectType = this.selectedProjectType.name;
        if (projectType === "flask" || projectType === "django") {
          this.syncModeButtons(projectType);
        }
      }
    } else if (step === 2) {
      prevBtn.style.display = "inline-block";
      nextBtn.style.display = "none";
      createBtn.style.display = "inline-block";

      // When going to step 2, make sure config is synced
      if (this.selectedProjectType) {
        this.updateConfigForCurrentMode();
      }
    }

    this.validateForm();
  }

  updatePreview() {
    const preview = document.getElementById("projectPreview");
    const projectName =
      document.getElementById("projectName").value || "my_project";
    const outputDir = document.getElementById("outputDir").value || "examples";

    if (!this.selectedProjectType) return;

    // Update preview info
    document.getElementById(
      "previewIcon"
    ).innerHTML = `<i class="${this.getProjectTypeIcon(
      this.selectedProjectType.name
    )}"></i>`;
    document.getElementById("previewName").textContent = projectName;
    document.getElementById(
      "previewPath"
    ).textContent = `${outputDir}/${projectName}`;

    // Update features
    const features = this.getProjectFeatures(this.selectedProjectType.name);
    const featuresContainer = document.getElementById("previewFeatures");
    featuresContainer.innerHTML = "";

    features.forEach((feature) => {
      const li = document.createElement("li");
      li.textContent = feature;
      featuresContainer.appendChild(li);
    });

    preview.style.display = "block";
  }
  getProjectFeatures(typeName) {
    if (typeName === "flask") {
      if (this.flaskMode === "custom") {
        return [
          "Cookiecutter Flask template",
          "Professional project structure",
          "Bandit security scanning",
          "Optimized Docker configuration",
          "Cache volumes for faster builds",
          "Comprehensive test setup",
          "Advanced CI/CD pipeline",
        ];
      } else {
        return [
          "Flask REST API with modular structure",
          "Docker and docker-compose",
          "Tests with pytest",
          "Basic CI/CD pipeline",
          "Health check endpoints",
        ];
      }
    }

    const features = {
      django: [
        "Cookiecutter Django template",
        "Admin panel and user management",
        "PostgreSQL database integration",
        "Docker containerization",
        "Security tools (Bandit, Safety)",
        "Pre-commit hooks",
        "Development settings optimization",
        "Complete CI/CD pipeline",
      ],
      node: [
        "Express.js REST API",
        "Health check endpoints",
        "Tests with Jest and Supertest",
        "ESLint code analysis",
        "Multi-stage Docker build",
        "Docker-compose orchestration",
        "Automated CI/CD pipeline",
      ],
      react: [
        "React 18 with Vite",
        "Optional TypeScript support",
        "React Router for navigation",
        "Tests with Vitest and Testing Library",
        "ESLint + Prettier configuration",
        "Multi-stage Docker build",
        "Security audit with npm audit",
        "Complete CI/CD pipeline",
      ],
    };
    return (
      features[typeName] || [
        "Base project structure",
        "Basic configuration",
        "CI/CD pipeline included",
      ]
    );
  }

  validateForm() {
    const nextBtn = document.getElementById("nextStepBtn");
    const createBtn = document.getElementById("createProjectBtn");

    if (this.currentStep === 1) {
      nextBtn.disabled = !this.selectedProjectType;
    } else if (this.currentStep === 2) {
      const projectName = document.getElementById("projectName").value.trim();
      const outputDir = document.getElementById("outputDir").value.trim();

      let isValid = false;

      if (
        (this.selectedProjectType &&
          this.selectedProjectType.name === "flask" &&
          this.flaskMode === "custom") ||
        (this.selectedProjectType &&
          this.selectedProjectType.name === "django" &&
          this.djangoMode === "custom")
      ) {
        console.log(
          `🔍 Validating ${this.selectedProjectType.name} custom mode...`
        );
        isValid = this.validateCookiecutterForm();
        console.log(
          `🔍 ${this.selectedProjectType.name} custom validation result:`,
          isValid
        );
      } else {
        console.log("🔍 Validating standard mode...");
        isValid = projectName && outputDir;
        console.log("🔍 Standard validation result:", isValid, {
          projectName,
          outputDir,
        });
      }

      createBtn.disabled = !isValid;

      if (projectName) {
        this.updatePreview();
      }
    }
  }

  handleFlaskModeChange() {
    console.log(`🔄 Flask mode changed to: ${this.flaskMode}`);

    if (this.flaskMode === "standard") {
      this.showStandardConfig();
    } else if (this.flaskMode === "custom") {
      this.showAdvancedConfig();
    }

    // Sync mode buttons
    this.syncModeButtons("flask");
    this.validateForm();
  }

  handleDjangoModeChange() {
    console.log(`🔄 Django mode changed to: ${this.djangoMode}`);

    if (this.djangoMode === "standard") {
      this.showStandardConfig();
    } else if (this.djangoMode === "custom") {
      this.showAdvancedConfig();
    }

    // Sync mode buttons
    this.syncModeButtons("django");
    this.validateForm();
  }

  handleReactLanguageChange() {
    console.log(`🔄 React language changed to: ${this.reactLanguage}`);

    // Update preview when language changes
    if (this.selectedProjectType && this.selectedProjectType.name === "react") {
      this.updatePreview();
    }

    this.validateForm();
  }

  showStandardConfig() {
    document.getElementById("standardConfig").style.display = "block";
    document.getElementById("advancedConfig").style.display = "none";
  }

  showAdvancedConfig() {
    document.getElementById("standardConfig").style.display = "none";
    document.getElementById("advancedConfig").style.display = "block";

    const currentConfig = this.getCurrentCookiecutterConfig();
    if (!currentConfig) {
      this.loadCookiecutterConfig();
    } else {
      this.renderCookiecutterForm();
    }
  }

  loadCookiecutterConfig() {
    const projectType = this.selectedProjectType
      ? this.selectedProjectType.name
      : "flask";
    console.log(`🔄 Loading cookiecutter config for ${projectType}...`);
    this.socket.emit("get_cookiecutter_config", {
      project_type: projectType,
    });
  }

  handleCookiecutterConfigResponse(data) {
    console.log("📋 Cookiecutter config response:", data);
    if (!data.success || data.error) {
      console.error("❌ Error loading cookiecutter config:", data.error);
      this.showCookiecutterError(data.error);
      return;
    }

    this.setCurrentCookiecutterConfig(data.fields);
    this.renderCookiecutterForm();
  }

  renderCookiecutterForm() {
    const formContainer = document.getElementById("cookiecutterForm");
    const currentConfig = this.getCurrentCookiecutterConfig();

    if (!currentConfig || !Array.isArray(currentConfig)) {
      formContainer.innerHTML =
        '<p class="text-muted">Could not load configuration.</p>';
      return;
    }

    let formHTML = '<div class="row g-3">';

    currentConfig.forEach((fieldConfig) => {
      formHTML += this.createFormField(fieldConfig);
    });

    formHTML += "</div>";
    formContainer.innerHTML = formHTML;

    // Add event listeners for dynamic inputs
    formContainer
      .querySelectorAll("input, select, textarea")
      .forEach((input) => {
        input.addEventListener("change", () => {
          this.validateForm();
          this.handleConditionalFields();
        });
        input.addEventListener("input", () => {
          this.validateForm();
          this.handleConditionalFields();
        });
      });

    this.handleConditionalFields();
  }

  createFormField(fieldConfig) {
    const {
      name,
      label,
      type,
      default: defaultValue,
      options,
      placeholder,
      required,
      depends_on,
      depends_value,
    } = fieldConfig;
    const fieldId = `cookiecutter_${name}`;

    let inputHTML = "";

    if (type === "select" && options && options.length > 0) {
      inputHTML = `
                <select class="form-select modern-input" id="${fieldId}" ${
        required ? "required" : ""
      }>
                    ${options
                      .map(
                        (option) =>
                          `<option value="${option.value}" ${
                            option.value === defaultValue ? "selected" : ""
                          }>${option.label}</option>`
                      )
                      .join("")}
                </select>
            `;
    } else if (type === "textarea") {
      inputHTML = `
                <textarea class="form-control modern-input" id="${fieldId}" 
                          rows="2" placeholder="${placeholder || ""}" ${
        required ? "required" : ""
      }>${defaultValue || ""}</textarea>
            `;
    } else if (type === "email") {
      inputHTML = `
                <input type="email" class="form-control modern-input" id="${fieldId}" 
                       value="${defaultValue || ""}" placeholder="${
        placeholder || ""
      }" ${required ? "required" : ""}>
            `;
    } else {
      inputHTML = `
                <input type="text" class="form-control modern-input" id="${fieldId}" 
                       value="${defaultValue || ""}" placeholder="${
        placeholder || ""
      }" ${required ? "required" : ""}>
            `;
    }

    const conditionalAttrs = depends_on
      ? `data-depends-on="${depends_on}" data-depends-value="${depends_value}" style="display: none;"`
      : "";

    return `
            <div class="col-md-6" ${conditionalAttrs}>
                <label for="${fieldId}" class="form-label fw-semibold">
                    ${label}
                    ${required ? '<span class="text-danger">*</span>' : ""}
                </label>
                ${inputHTML}
            </div>
        `;
  }

  showCookiecutterError(error) {
    const formContainer = document.getElementById("cookiecutterForm");
    formContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading configuration: ${error}
                <br><small>Using standard configuration.</small>
            </div>
        `;
  }

  handleConditionalFields() {
    const currentConfig = this.getCurrentCookiecutterConfig();
    if (!currentConfig) return;

    currentConfig.forEach((fieldConfig) => {
      if (fieldConfig.depends_on && fieldConfig.depends_value) {
        const dependentField = document.querySelector(
          `[data-depends-on="${fieldConfig.depends_on}"]`
        );
        const parentField = document.getElementById(
          `cookiecutter_${fieldConfig.depends_on}`
        );

        if (dependentField && parentField) {
          const parentValue = parentField.value;
          const shouldShow = parentValue === fieldConfig.depends_value;

          dependentField.style.display = shouldShow ? "block" : "none";

          if (!shouldShow) {
            const input = dependentField.querySelector(
              "input, select, textarea"
            );
            if (input) input.value = "";
          }
        }
      }
    });
  }

  validateCookiecutterForm() {
    const currentConfig = this.getCurrentCookiecutterConfig();
    if (!currentConfig || !Array.isArray(currentConfig)) {
      return false;
    }

    for (const fieldConfig of currentConfig) {
      if (fieldConfig.required) {
        const fieldId = `cookiecutter_${fieldConfig.name}`;
        const field = document.getElementById(fieldId);

        if (!field) {
          console.warn(`Required field ${fieldId} not found`);
          return false;
        }

        const value = field.value ? field.value.trim() : "";
        if (!value) {
          console.log(`Required field ${fieldConfig.name} is empty`);
          return false;
        }

        // Allow spaces in project_name, but require app_name to be valid identifier
        if (
          fieldConfig.name === "app_name" &&
          !/^[a-zA-Z0-9_-]+$/.test(value)
        ) {
          console.log(
            `Invalid format for app_name (must be valid identifier): ${value}`
          );
          return false;
        }
      }
    }

    console.log("✅ Cookiecutter form validation passed");
    return true;
  }

  createProject() {
    if (!this.selectedProjectType) {
      alert("Please select a project type");
      return;
    }

    this.showCreationProgress();

    let requestData = {
      project_type: this.selectedProjectType.name,
    };

    if (
      (this.selectedProjectType.name === "flask" &&
        this.flaskMode === "custom") ||
      (this.selectedProjectType.name === "django" &&
        this.djangoMode === "custom")
    ) {
      const customConfig = this.collectCookiecutterConfig();
      const outputDir =
        document.getElementById("outputDir").value.trim() || "examples";

      if (!customConfig.project_name) {
        alert('Please complete the "Project name" field');
        return;
      }

      requestData.project_name = customConfig.project_name;
      requestData.output_dir = outputDir;
      requestData.custom_config = customConfig;
      requestData.interactive = false;

      console.log("🚀 Sending advanced project request:", requestData);
      this.socket.emit("create_project_advanced", requestData);
    } else {
      const projectName = document.getElementById("projectName").value.trim();
      const outputDir = document.getElementById("outputDir").value.trim();

      if (!projectName) {
        alert("Please specify the project name");
        return;
      }
      if (!outputDir) {
        alert("Please specify the target directory");
        return;
      }

      requestData.project_name = projectName;
      requestData.output_dir = outputDir;

      // Add React-specific parameters if applicable
      if (this.selectedProjectType.name === "react") {
        requestData.react_language = this.reactLanguage;
        requestData.react_port = this.reactPort;
        console.log(
          `⚛️ Adding React parameters: language=${this.reactLanguage}, port=${this.reactPort}`
        );
      }

      console.log("🚀 Sending project request:", requestData);
      this.socket.emit("create_project", requestData);
    }
  }

  collectCookiecutterConfig() {
    const config = {};
    const currentConfig = this.getCurrentCookiecutterConfig();

    if (!currentConfig || !Array.isArray(currentConfig)) {
      return config;
    }

    currentConfig.forEach((fieldConfig) => {
      const fieldId = `cookiecutter_${fieldConfig.name}`;
      const field = document.getElementById(fieldId);

      if (field && field.offsetParent !== null) {
        if (field.type === "checkbox") {
          config[fieldConfig.name] = field.checked;
        } else {
          const value = field.value ? field.value.trim() : "";
          if (value) {
            config[fieldConfig.name] = value;
          } else if (fieldConfig.default) {
            config[fieldConfig.name] = fieldConfig.default;
          }
        }
      }
    });

    console.log("🔧 Collected cookiecutter config:", config);
    return config;
  }

  showCreationProgress() {
    const progressSection = document.getElementById("creationProgressSection");
    progressSection.style.display = "block";
    progressSection.scrollIntoView({ behavior: "smooth" });

    document.querySelectorAll(".step-item").forEach((step) => {
      step.classList.remove("active", "completed");
      const icon = step.querySelector(".step-icon");
      icon.className = "fas fa-circle step-icon";
    });

    const logsContainer = document.getElementById("projectCreationLogs");
    logsContainer.innerHTML =
      '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin me-1"></i>Starting creation...</div>';
  }

  handleProjectCreationUpdate(data) {
    console.log("Project creation update:", data);

    const {
      creating,
      progress,
      current_step,
      log,
      steps,
      success,
      error,
      project_name,
    } = data;

    // Update progress bar
    if (progress !== undefined) {
      const progressBar = document.getElementById("creationProgressBar");
      const progressPercentage = document.getElementById("progressPercentage");
      const progressText = document.getElementById("progressText");

      if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute("aria-valuenow", progress);
      }

      if (progressPercentage) {
        progressPercentage.textContent = `${progress}%`;
      }

      if (progressText && current_step) {
        progressText.textContent = current_step;
      }
    }

    // Update current step text
    if (current_step) {
      const stepText = document.getElementById("progressText");
      if (stepText) {
        stepText.textContent = current_step;
      }
    }

    // Update logs
    if (log && Array.isArray(log)) {
      const logsContainer = document.getElementById("projectCreationLogs");
      if (logsContainer) {
        logsContainer.innerHTML = log
          .map((logEntry) => `<div class="log-entry">${logEntry}</div>`)
          .join("");
        logsContainer.scrollTop = logsContainer.scrollHeight;
      }
    }

    // Update step indicators
    if (steps && Array.isArray(steps)) {
      steps.forEach((step, index) => {
        const stepElement = document.querySelector(
          `.step-item:nth-child(${index + 1})`
        );
        if (stepElement) {
          const icon = stepElement.querySelector(".step-icon");
          stepElement.classList.remove("active", "completed");

          if (step.status === "running") {
            stepElement.classList.add("active");
            icon.className = "fas fa-spinner fa-spin step-icon";
          } else if (step.status === "success") {
            stepElement.classList.add("completed");
            icon.className = "fas fa-check step-icon";
          } else if (step.status === "failure") {
            icon.className = "fas fa-times step-icon";
          }
        }
      });
    } // Handle completion
    if (success) {
      // Update projects count from server since a new project was created
      this.updateStats();

      const successMessage = document.getElementById("successMessage");
      if (successMessage) {
        successMessage.style.display = "block";
        if (project_name) {
          successMessage.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Project "${project_name}" created successfully!
                        </div>
                    `;
        }
      }
    }

    // Handle error
    if (error) {
      const errorMessage = document.getElementById("errorMessage");
      if (errorMessage) {
        errorMessage.style.display = "block";
        errorMessage.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        Error: ${error}
                    </div>
                `;
      }
    }
  }
  updateStats() {
    // Update available templates count
    const templatesElement = document.getElementById("availableTemplates");
    if (templatesElement) {
      templatesElement.textContent = this.projectTypes.length || 0;
    }

    // Update projects count from server
    this.getProjectsCreatedCount();

    console.log(
      `📊 Stats updated: ${this.projectTypes.length} templates available`
    );
  }
  getProjectsCreatedCount() {
    // Fetch real projects count from server
    fetch("/api/projects/count")
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          const createdElement = document.getElementById("projectsCreated");
          if (createdElement) {
            createdElement.textContent = data.count;
          }
          console.log(`📊 Projects count updated: ${data.count} existing`);
        } else {
          console.warn("Error fetching projects count:", data.error);
          // Fallback to 0 if there's an error
          const createdElement = document.getElementById("projectsCreated");
          if (createdElement) {
            createdElement.textContent = "0";
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching projects count:", error);
        // Fallback to 0 if there's an error
        const createdElement = document.getElementById("projectsCreated");
        if (createdElement) {
          createdElement.textContent = "0";
        }
      });
  }

  startStatsTimer() {
    // Update stats immediately
    this.updateStats();

    // Set up periodic updates every 30 seconds
    this.statsTimer = setInterval(() => {
      this.updateStats();
      console.log("📊 Periodic stats update completed");
    }, 30000);

    console.log("⏱️ Stats timer started - updating every 30 seconds");
  }

  stopStatsTimer() {
    if (this.statsTimer) {
      clearInterval(this.statsTimer);
      this.statsTimer = null;
      console.log("⏹️ Stats timer stopped");
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.projectsUI = new ProjectsUI();
});
