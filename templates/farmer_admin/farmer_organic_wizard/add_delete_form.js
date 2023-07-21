<script>
    
    function addForm(e){
        e.preventDefault()

        let formset_form = document.querySelectorAll(".formset_form")
        let container = document.querySelector("#form-container")
        let addButtonContainer = document.querySelector("#add-new-button-container")
        let totalForms = $("#id_{{wizard_current_step}}-TOTAL_FORMS")
        let formNum = formset_form.length - 1

        let newForm = formset_form[0].cloneNode(true)
        let formRegex = RegExp(`{{wizard_current_step}}-(\\d){1}-`,'g')

        formNum++
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `{{wizard_current_step}}-${formNum}-`)
        if (formNum >= 1){
            var html = `
            <button class="btn btn-primary" onClick="deleteForm('form_${formNum}')" type="button">
                <i class="bi bi-trash fs-2"></i>
            </button>
            `
            newForm.querySelector('.delete-button').innerHTML = html 
        }
        newForm.id = `form_${formNum}`
        inputs = newForm.querySelectorAll('.form-control')
        for (i = 0; i < inputs.length; i++) {
            var input = inputs[i]
            if (input) {
                switch (input.type) {
                    case 'select-one':
                        input.value = ''
                    case 'button':
                    case 'text':
                    case 'submit':
                    case 'password':
                    case 'file':
                    case 'email':
                    case 'date':
                    case 'number':
                        input.value = '';
                    case 'checkbox':
                    case 'radio':
                        input.checked = false;
                }
            }
        }
        container.insertBefore(newForm, addButtonContainer)
        totalForms.val(formNum+1)
        totalForms.trigger('change')
    }

    function deleteForm(id){
        let formset_form = document.querySelectorAll(".formset_form")
        let totalForms = $("#id_{{wizard_current_step}}-TOTAL_FORMS")
        let formNum = formset_form.length - 1

        let form = document.getElementById(id)
        form.parentNode.removeChild(form)
        totalForms.val(formNum)
        totalForms.trigger('change')
    }

</script>