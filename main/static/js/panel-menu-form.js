(function () {
    const form = document.querySelector('.panel-form--menu');
    if (!form) return;

    const prefix = form.dataset.variantPrefix || 'variants';
    const minRows = parseInt(form.dataset.minVariantRows || '2', 10);
    const singleBlock = form.querySelector('[data-pricing="single"]');
    const volumesBlock = form.querySelector('[data-pricing="volumes"]');
    const radios = form.querySelectorAll('input[name="pricing_mode"]');
    const rowsContainer = form.querySelector('[data-variant-rows]');
    const emptyTemplate = form.querySelector('[data-variant-empty]');
    const addButton = form.querySelector('[data-add-variant]');

    function totalFormsInput() {
        return form.querySelector(`#id_${prefix}-TOTAL_FORMS`);
    }

    function currentMode() {
        const checked = form.querySelector('input[name="pricing_mode"]:checked');
        return checked ? checked.value : 'single';
    }

    function activeRows() {
        return Array.from(rowsContainer.querySelectorAll('[data-variant-row]')).filter(
            (row) => row.dataset.removed !== 'true'
        );
    }

    function reindexRows() {
        const rows = activeRows();
        rows.forEach((row, index) => {
            row.querySelectorAll('input, select, textarea').forEach((input) => {
                if (!input.name) return;
                input.name = input.name.replace(new RegExp(`${prefix}-\\d+-`), `${prefix}-${index}-`);
                if (input.id) {
                    input.id = input.id.replace(new RegExp(`${prefix}-\\d+-`), `${prefix}-${index}-`);
                }
            });
            row.querySelectorAll('label[for]').forEach((label) => {
                const target = label.getAttribute('for');
                if (target) {
                    label.setAttribute('for', target.replace(new RegExp(`${prefix}-\\d+-`), `${prefix}-${index}-`));
                }
            });
        });
        const totalInput = totalFormsInput();
        if (totalInput) {
            totalInput.value = String(rows.length);
        }
    }

    function addVariantRow() {
        if (!emptyTemplate || !rowsContainer) return;
        const clone = emptyTemplate.content.cloneNode(true);
        const row = clone.querySelector('[data-variant-row]');
        if (!row) return;
        rowsContainer.appendChild(row);
        reindexRows();
        updateRemoveButtons();
    }

    function removeVariantRow(row) {
        const idInput = row.querySelector(`input[name$="-id"]`);
        const deleteInput = row.querySelector(`input[name$="-DELETE"]`);
        if (idInput && idInput.value) {
            if (deleteInput) {
                deleteInput.value = 'on';
            }
            row.dataset.removed = 'true';
            row.hidden = true;
            row.querySelectorAll('input:not([type="hidden"]), select, textarea').forEach((input) => {
                input.value = '';
            });
        } else {
            row.remove();
        }
        reindexRows();
        updateRemoveButtons();
    }

    function ensureMinRows() {
        if (currentMode() !== 'volumes' || !rowsContainer) return;
        const target = minRows > 0 ? minRows : 0;
        while (activeRows().length < target) {
            addVariantRow();
        }
        updateRemoveButtons();
    }

    function updateRemoveButtons() {
        const rows = activeRows();
        const canRemove = rows.length > Math.max(minRows, 1);
        rows.forEach((row) => {
            const button = row.querySelector('[data-variant-remove]');
            if (button) {
                button.hidden = !canRemove;
            }
        });
    }

    function updatePricingBlocks() {
        const isSingle = currentMode() === 'single';
        if (singleBlock) singleBlock.hidden = !isSingle;
        if (volumesBlock) volumesBlock.hidden = isSingle;
        if (!isSingle) {
            ensureMinRows();
        }
        updateRemoveButtons();
    }

    if (rowsContainer) {
        rowsContainer.addEventListener('click', (event) => {
            const button = event.target.closest('[data-variant-remove]');
            if (!button) return;
            const row = button.closest('[data-variant-row]');
            if (row) {
                removeVariantRow(row);
            }
        });
    }

    if (addButton) {
        addButton.addEventListener('click', () => {
            addVariantRow();
        });
    }

    radios.forEach((radio) => radio.addEventListener('change', updatePricingBlocks));
    updatePricingBlocks();
})();
