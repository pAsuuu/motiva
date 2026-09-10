// Motiva Enterprise Pro Client Logic

let cvData = {
  raw_text: "",
  contact: {
    name: "Dany Ferreira",
    headline: "Assistant Chef de Projet Marketing",
    email: "dany.ferreira@epitech.digital",
    phone: "06 99 88 77 66",
    location: "Paris, France"
  }
};

let currentTheme = "modern";

document.addEventListener("DOMContentLoaded", () => {
  initSettings();
  initContactTwoWaySync();
  initCVUpload();
  initTabs();
  initToneSelector();
  initThemeButtons();
  initActions();
  initJobInputWatchers();
  checkBackendStatus();
});

// Two-way synchronization between contact form and A4 sheet
function initContactTwoWaySync() {
  const fields = [
    { inputId: "contact-name", docId: "doc-candidate-name", key: "name", extraDocId: "doc-signature" },
    { inputId: "contact-headline", docId: "doc-candidate-headline", key: "headline" },
    { inputId: "contact-email", docId: "doc-candidate-email", key: "email" },
    { inputId: "contact-phone", docId: "doc-candidate-phone", key: "phone" },
    { inputId: "contact-location", docId: "doc-candidate-location", key: "location" }
  ];

  fields.forEach(f => {
    const inputEl = document.getElementById(f.inputId);
    const docEl = document.getElementById(f.docId);
    if (inputEl && cvData.contact[f.key]) {
      inputEl.value = cvData.contact[f.key];
    }
    if (docEl && cvData.contact[f.key]) {
      docEl.textContent = cvData.contact[f.key];
    }
    if (f.extraDocId && cvData.contact[f.key]) {
      const extra = document.getElementById(f.extraDocId);
      if (extra) extra.textContent = cvData.contact[f.key];
    }

    if (inputEl) {
      inputEl.addEventListener("input", () => {
        const val = inputEl.value.trim();
        cvData.contact[f.key] = val;
        if (docEl) docEl.textContent = val || " ";
        if (f.extraDocId) {
          const extra = document.getElementById(f.extraDocId);
          if (extra) extra.textContent = val || " ";
        }
      });
    }

    if (docEl) {
      docEl.addEventListener("input", () => {
        const val = docEl.innerText.trim();
        cvData.contact[f.key] = val;
        if (inputEl) inputEl.value = val;
        if (f.extraDocId) {
          const extra = document.getElementById(f.extraDocId);
          if (extra) extra.textContent = val;
        }
      });
    }
  });
}

function updateContactFields(contact) {
  if (!contact) return;
  const fields = [
    { inputId: "contact-name", docId: "doc-candidate-name", key: "name", extraDocId: "doc-signature" },
    { inputId: "contact-headline", docId: "doc-candidate-headline", key: "headline" },
    { inputId: "contact-email", docId: "doc-candidate-email", key: "email" },
    { inputId: "contact-phone", docId: "doc-candidate-phone", key: "phone" },
    { inputId: "contact-location", docId: "doc-candidate-location", key: "location" }
  ];

  fields.forEach(f => {
    if (contact[f.key]) {
      cvData.contact[f.key] = contact[f.key];
      const inputEl = document.getElementById(f.inputId);
      const docEl = document.getElementById(f.docId);
      if (inputEl) inputEl.value = contact[f.key];
      if (docEl) docEl.textContent = contact[f.key];
      if (f.extraDocId) {
        const extra = document.getElementById(f.extraDocId);
        if (extra) extra.textContent = contact[f.key];
      }
    }
  });
}

// Watch job inputs to clean and synchronize title & company in real time
function initJobInputWatchers() {
  const compInput = document.getElementById("company-name");
  const titleInput = document.getElementById("job-title");

  let timeout = null;
  const triggerJobAnalysis = () => {
    clearTimeout(timeout);
    timeout = setTimeout(async () => {
      const rawTitle = titleInput.value.trim();
      const rawComp = compInput.value.trim();
      if (!rawTitle && !rawComp) return;

      try {
        const res = await fetch("/api/analyze-job", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ raw_title: rawTitle, company_name: rawComp })
        });
        const data = await res.json();

        if (data.clean_title && data.clean_title !== rawTitle) {
          titleInput.value = data.clean_title;
        }
        if (data.company_name && !compInput.value.trim()) {
          compInput.value = data.company_name;
        }

        // Update A4 Sheet
        if (data.company_name) {
          document.getElementById("doc-recipient-company").textContent = data.company_name;
        }
        if (data.department) {
          document.getElementById("doc-recipient-department").textContent = data.department;
        }
        if (data.clean_subject) {
          document.getElementById("doc-subject").textContent = data.clean_subject;
        }

        // Show analysis card
        displayJobAnalysis(data);

      } catch (e) {
        console.warn("Analyse auto:", e);
      }
    }, 600);
  };

  titleInput.addEventListener("input", triggerJobAnalysis);
  compInput.addEventListener("input", triggerJobAnalysis);
}

function displayJobAnalysis(data) {
  const card = document.getElementById("job-analysis-card");
  const bContract = document.getElementById("badge-contract");
  const aCompany = document.getElementById("analysis-company");
  const aTitle = document.getElementById("analysis-title");
  const aDept = document.getElementById("analysis-dept");

  if (!card) return;

  if (data.clean_title || data.company_name) {
    if (aCompany) aCompany.textContent = data.company_name || "Entreprise identifiée";
    if (aTitle) aTitle.textContent = data.clean_title || "Poste épuré";
    if (aDept) aDept.textContent = data.department || "Direction";
    if (bContract) bContract.textContent = data.contract_type || "Poste Clé";
    card.classList.remove("hidden");
  }
}

// Check API status
async function checkBackendStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    const storedKey = localStorage.getItem("motiva_gemini_api_key");
    const statusLabel = document.getElementById("api-status-label");
    const statusDot = document.getElementById("api-status-dot");
    if (storedKey || data.has_env_key) {
      statusLabel.textContent = "IA Opérationnelle";
      statusLabel.classList.add("text-emerald-400", "font-semibold");
      statusDot.className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
    } else {
      statusLabel.textContent = "Mode Démo (Clé IA dispo)";
      statusDot.className = "w-2 h-2 rounded-full bg-amber-400";
    }
  } catch (e) {
    console.warn("Backend status check error:", e);
  }
}

// Settings Modal
function initSettings() {
  const modal = document.getElementById("settings-modal");
  const btnOpen = document.getElementById("btn-open-settings");
  const btnClose = document.getElementById("btn-close-settings");
  const btnSave = document.getElementById("btn-save-settings");
  const inputKey = document.getElementById("input-api-key");
  const selectModel = document.getElementById("select-model");

  modal.classList.add("hidden");
  modal.classList.remove("flex");

  inputKey.value = localStorage.getItem("motiva_gemini_api_key") || "";
  selectModel.value = localStorage.getItem("motiva_gemini_model") || "gemini-2.5-flash";

  btnOpen.addEventListener("click", () => {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  });

  const closeModal = () => {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  };

  btnClose.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  btnSave.addEventListener("click", () => {
    localStorage.setItem("motiva_gemini_api_key", inputKey.value.trim());
    localStorage.setItem("motiva_gemini_model", selectModel.value);
    closeModal();
    checkBackendStatus();
  });
}

// CV Upload & Parsing
function initCVUpload() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("cv-file-input");
  const cvInfoCard = document.getElementById("cv-info-card");
  const cvFilename = document.getElementById("cv-filename");
  const cvStatus = document.getElementById("cv-status");
  const btnToggleCv = document.getElementById("btn-toggle-cv-text");
  const cvExtractedText = document.getElementById("cv-extracted-text");

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("border-blue-500", "bg-blue-50/50");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleCVUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleCVUpload(e.target.files[0]);
    }
  });

  btnToggleCv.addEventListener("click", () => {
    cvExtractedText.classList.toggle("hidden");
  });

  async function handleCVUpload(file) {
    cvStatus.textContent = "Extraction en cours...";
    cvStatus.className = "text-xs text-blue-600 font-semibold animate-pulse";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload-cv", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Erreur de parsing");

      const data = await res.json();
      cvData.raw_text = data.raw_text || "";

      updateContactFields(data.contact);

      cvFilename.textContent = data.filename;
      cvExtractedText.value = data.raw_text;

      cvInfoCard.classList.remove("hidden");
      cvStatus.textContent = "CV Prêt & Coordonnées à jour ✓";
      cvStatus.className = "text-xs text-emerald-600 font-bold";

    } catch (err) {
      cvStatus.textContent = "Erreur de lecture";
      cvStatus.className = "text-xs text-rose-600 font-bold";
      alert("Impossible de lire ce document. Essayez un format PDF, Word ou texte brut.");
    }
  }
}

// Tabs: URL vs Paste Text
function initTabs() {
  const tabUrl = document.getElementById("tab-url");
  const tabText = document.getElementById("tab-text");
  const paneUrl = document.getElementById("pane-url");
  const paneText = document.getElementById("pane-text");
  const btnFetchUrl = document.getElementById("btn-fetch-url");
  const urlInput = document.getElementById("job-url");
  const fetchUrlLabel = document.getElementById("fetch-url-label");
  const urlFeedback = document.getElementById("url-feedback");

  tabUrl.addEventListener("click", () => {
    tabUrl.className = "py-1.5 px-3 font-bold text-blue-600 border-b-2 border-blue-600 focus:outline-none transition";
    tabText.className = "py-1.5 px-3 font-medium text-slate-500 hover:text-slate-800 focus:outline-none transition";
    paneUrl.classList.remove("hidden");
    paneText.classList.add("hidden");
  });

  tabText.addEventListener("click", () => {
    tabText.className = "py-1.5 px-3 font-bold text-blue-600 border-b-2 border-blue-600 focus:outline-none transition";
    tabUrl.className = "py-1.5 px-3 font-medium text-slate-500 hover:text-slate-800 focus:outline-none transition";
    paneText.classList.remove("hidden");
    paneUrl.classList.add("hidden");
  });

  btnFetchUrl.addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) return;

    fetchUrlLabel.textContent = "Analyse...";
    urlFeedback.textContent = "Épuration du titre & analyse stratégique de l'entreprise...";
    urlFeedback.className = "text-[11px] text-blue-600 animate-pulse font-medium";

    try {
      const res = await fetch("/api/fetch-job", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
      const data = await res.json();

      if (data.success && data.text) {
        document.getElementById("job-text").value = data.text;

        // Auto-populate clean title & company
        if (data.clean_title) {
          document.getElementById("job-title").value = data.clean_title;
        }
        if (data.company_name) {
          document.getElementById("company-name").value = data.company_name;
        }

        // Update A4 Sheet immediately
        if (data.company_name) {
          document.getElementById("doc-recipient-company").textContent = data.company_name;
        }
        if (data.department) {
          document.getElementById("doc-recipient-department").textContent = data.department;
        }
        if (data.clean_subject) {
          document.getElementById("doc-subject").textContent = data.clean_subject;
        }

        // Show analysis card
        displayJobAnalysis(data);

        urlFeedback.textContent = `Offre analysée avec succès ! Poste épuré : "${data.clean_title}"`;
        urlFeedback.className = "text-[11px] text-emerald-600 font-bold";
      } else {
        urlFeedback.textContent = data.error || "Extraction automatique impossible.";
        urlFeedback.className = "text-[11px] text-amber-600";
      }
    } catch (e) {
      urlFeedback.textContent = "Erreur lors de la récupération de l'URL.";
      urlFeedback.className = "text-[11px] text-rose-600";
    } finally {
      fetchUrlLabel.textContent = "Analyser l'Offre";
    }
  });
}

// Tone selector
function initToneSelector() {
  const cards = document.querySelectorAll(".tone-card");
  cards.forEach(card => {
    card.addEventListener("click", () => {
      cards.forEach(c => {
        c.classList.remove("border-blue-600", "bg-blue-50/70", "shadow-sm");
        c.classList.add("border-slate-200");
        c.querySelector("input").checked = false;
      });
      card.classList.remove("border-slate-200");
      card.classList.add("border-blue-600", "bg-blue-50/70", "shadow-sm");
      card.querySelector("input").checked = true;
    });
  });
}

// Theme buttons
function initThemeButtons() {
  const sheet = document.getElementById("print-area");
  const buttons = document.querySelectorAll(".theme-btn");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      const theme = btn.getAttribute("data-theme");
      currentTheme = theme;

      buttons.forEach(b => {
        b.className = "theme-btn px-3 py-1 rounded-lg font-medium border border-white/10 text-slate-400 hover:bg-white/5 text-[11px] transition";
      });
      btn.className = "theme-btn px-3 py-1 rounded-lg font-semibold border border-blue-500 bg-blue-500/20 text-blue-300 text-[11px] transition";

      sheet.classList.remove("theme-modern", "theme-executive", "theme-minimal");
      sheet.classList.add(`theme-${theme}`);
    });
  });
}

// Main Actions: Generation, Export PDF, Copy
function initActions() {
  const btnGenerate = document.getElementById("btn-generate");
  const progressBox = document.getElementById("generation-progress");
  const progressStep = document.getElementById("progress-step");
  const btnDownloadPdf = document.getElementById("btn-download-pdf");
  const btnCopyText = document.getElementById("btn-copy-text");

  btnGenerate.addEventListener("click", async () => {
    const companyName = document.getElementById("company-name").value.trim();
    const jobTitle = document.getElementById("job-title").value.trim();
    const jobText = document.getElementById("job-text").value.trim();
    const customNotes = document.getElementById("custom-notes").value.trim();
    const selectedToneRadio = document.querySelector('input[name="tone"]:checked');
    const tone = selectedToneRadio ? selectedToneRadio.value : "direct_authentic";

    if (!cvData.raw_text && !document.getElementById("cv-extracted-text").value) {
      alert("Veuillez d'abord déposer votre CV ou renseigner vos informations.");
      return;
    }
    if (!companyName) {
      alert("Veuillez indiquer le nom de l'entreprise cible.");
      document.getElementById("company-name").focus();
      return;
    }

    const cvTextToUse = cvData.raw_text || document.getElementById("cv-extracted-text").value || "Expérience riche et diversifiée";

    btnGenerate.disabled = true;
    progressBox.classList.remove("hidden");
    progressStep.textContent = "1/3 : Renseignement approfondi sur l'actualité & l'équipe...";

    try {
      let researchInsightsText = "";
      try {
        const researchRes = await fetch("/api/research-company", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ company_name: companyName, job_text: jobText })
        });
        const researchData = await researchRes.json();
        researchInsightsText = researchData.raw_insights || "";
      } catch (e) {}

      progressStep.textContent = "2/3 : Épuration du titre, analyse des synergies & Élimination des clichés...";

      const apiKey = localStorage.getItem("motiva_gemini_api_key") || "";
      const modelName = localStorage.getItem("motiva_gemini_model") || "gemini-2.5-flash";

      progressStep.textContent = "3/3 : Rédaction haute fidélité & mise en page A4...";

      const genRes = await fetch("/api/generate-letter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cv_text: cvTextToUse,
          company_name: companyName,
          job_title: jobTitle,
          job_text: jobText,
          company_research: researchInsightsText,
          candidate_contact: cvData.contact,
          custom_notes: customNotes,
          tone: tone,
          api_key: apiKey,
          model_name: modelName
        })
      });

      if (!genRes.ok) {
        const err = await genRes.json();
        throw new Error(err.detail || "Erreur de génération");
      }

      const letterData = await genRes.json();

      // Populate Live Document while STRICTLY preserving candidate contacts and clean titles
      populateDocument(letterData);

      // Smooth scroll to preview
      document.getElementById("print-area").scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (err) {
      alert("Erreur lors de la génération : " + err.message);
    } finally {
      btnGenerate.disabled = false;
      progressBox.classList.add("hidden");
    }
  });

  function populateDocument(data) {
    const cand = data.candidate || {};
    const recip = data.recipient || {};
    const meta = data.meta || {};
    const content = data.letter_content || {};

    if (cand.name) {
      document.getElementById("doc-candidate-name").textContent = cand.name;
      document.getElementById("doc-signature").textContent = cand.name;
      document.getElementById("contact-name").value = cand.name;
    }
    if (cand.headline) {
      document.getElementById("doc-candidate-headline").textContent = cand.headline;
      document.getElementById("contact-headline").value = cand.headline;
    }
    if (cand.email) {
      document.getElementById("doc-candidate-email").textContent = cand.email;
      document.getElementById("contact-email").value = cand.email;
    }
    if (cand.phone) {
      document.getElementById("doc-candidate-phone").textContent = cand.phone;
      document.getElementById("contact-phone").value = cand.phone;
    }
    if (cand.location) {
      document.getElementById("doc-candidate-location").textContent = cand.location;
      document.getElementById("contact-location").value = cand.location;
    }

    if (recip.company) document.getElementById("doc-recipient-company").textContent = recip.company;
    if (recip.department) document.getElementById("doc-recipient-department").textContent = recip.department;
    if (recip.city) document.getElementById("doc-recipient-city").textContent = recip.city;

    if (meta.date) document.getElementById("doc-date").textContent = meta.date;
    if (meta.subject) document.getElementById("doc-subject").textContent = meta.subject;

    if (content.salutation) document.getElementById("doc-salutation").textContent = content.salutation;
    if (content.paragraph_hook) document.getElementById("doc-para-hook").textContent = content.paragraph_hook;
    if (content.paragraph_experience) document.getElementById("doc-para-experience").textContent = content.paragraph_experience;
    if (content.paragraph_team_fit) document.getElementById("doc-para-team").textContent = content.paragraph_team_fit;
    if (content.paragraph_call_to_action) document.getElementById("doc-para-cta").textContent = content.paragraph_call_to_action;
    if (content.valediction) document.getElementById("doc-valediction").textContent = content.valediction;

    if (data.match_score) {
      document.getElementById("match-score-badge").textContent = `Match : ${data.match_score}%`;
    }

    if (data.research_insights && data.research_insights.length > 0) {
      const el1 = document.getElementById("insight-1");
      const el2 = document.getElementById("insight-2");
      if (el1 && data.research_insights[0]) el1.textContent = data.research_insights[0];
      if (el2 && data.research_insights[1]) el2.textContent = data.research_insights[1];
    }
  }

  function gatherCurrentDocumentData() {
    return {
      candidate: {
        name: document.getElementById("doc-candidate-name").innerText.trim(),
        headline: document.getElementById("doc-candidate-headline").innerText.trim(),
        email: document.getElementById("doc-candidate-email").innerText.trim(),
        phone: document.getElementById("doc-candidate-phone").innerText.trim(),
        location: document.getElementById("doc-candidate-location").innerText.trim(),
      },
      recipient: {
        company: document.getElementById("doc-recipient-company").innerText.trim(),
        department: document.getElementById("doc-recipient-department").innerText.trim(),
        city: document.getElementById("doc-recipient-city").innerText.trim(),
      },
      meta: {
        date: document.getElementById("doc-date").innerText.trim(),
        subject: document.getElementById("doc-subject").innerText.trim(),
      },
      letter_content: {
        salutation: document.getElementById("doc-salutation").innerText.trim(),
        paragraph_hook: document.getElementById("doc-para-hook").innerText.trim(),
        paragraph_experience: document.getElementById("doc-para-experience").innerText.trim(),
        paragraph_team_fit: document.getElementById("doc-para-team").innerText.trim(),
        paragraph_call_to_action: document.getElementById("doc-para-cta").innerText.trim(),
        valediction: document.getElementById("doc-valediction").innerText.trim(),
        signature: document.getElementById("doc-signature").innerText.trim(),
      }
    };
  }

  // Export PDF
  btnDownloadPdf.addEventListener("click", async () => {
    btnDownloadPdf.disabled = true;
    const origHtml = btnDownloadPdf.innerHTML;
    btnDownloadPdf.innerHTML = `<span>Génération du PDF...</span>`;

    const letterData = gatherCurrentDocumentData();

    try {
      const response = await fetch("/api/export-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          letter_data: letterData,
          theme: currentTheme
        })
      });

      if (!response.ok) throw new Error("Erreur serveur lors de la création du PDF");

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      const candName = (letterData.candidate.name || "Candidat").replace(/\s+/g, "_");
      const compName = (letterData.recipient.company || "Candidature").replace(/\s+/g, "_");
      a.download = `Lettre_Motivation_${candName}_${compName}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);

    } catch (err) {
      if (confirm("Génération serveur indisponible. Souhaitez-vous imprimer / enregistrer en PDF via votre navigateur ?")) {
        window.print();
      }
    } finally {
      btnDownloadPdf.disabled = false;
      btnDownloadPdf.innerHTML = origHtml;
    }
  });

  // Copy text
  btnCopyText.addEventListener("click", () => {
    const data = gatherCurrentDocumentData();
    const fullText = `
${data.candidate.name}
${data.candidate.headline}
Email: ${data.candidate.email} | Tél: ${data.candidate.phone} | ${data.candidate.location}

${data.recipient.company}
${data.recipient.department}
${data.recipient.city}

${data.meta.date}

${data.meta.subject}

${data.letter_content.salutation}

${data.letter_content.paragraph_hook}

${data.letter_content.paragraph_experience}

${data.letter_content.paragraph_team_fit}

${data.letter_content.paragraph_call_to_action}

${data.letter_content.valediction}
${data.letter_content.signature}
    `.trim();

    navigator.clipboard.writeText(fullText).then(() => {
      const orig = btnCopyText.innerHTML;
      btnCopyText.innerHTML = `<span class="text-emerald-400 font-bold">Copié ✓</span>`;
      setTimeout(() => btnCopyText.innerHTML = orig, 2000);
    });
  });
}
