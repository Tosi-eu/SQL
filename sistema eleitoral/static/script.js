function showFields() {
    var entity = document.getElementById("entity").value;
    var fields = document.querySelectorAll(".entity-fields");
    fields.forEach(field => field.style.display = "none");

    if (entity) {
        var entityFields = document.getElementById(entity + "-fields");
        if (entityFields) {
            entityFields.style.display = "block";
        }
    }
}

function toggleDoadorFields() {
        var tipoDoador = document.getElementById("tipo_doador").value;
        var cpfField = document.getElementById("cpf_field");
        var cnpjField = document.getElementById("cnpj_field");

        if (tipoDoador == "Físico") {
            cpfField.style.display = "block";
            cnpjField.style.display = "none";
        } else if (tipoDoador == "Jurídico") {
            cpfField.style.display = "block";
            cnpjField.style.display = "none";
        } else {
            cpfField.style.display = "none";
            cnpjField.style.display = "none";
        }
    }

    function toggleForm() {
        var doadorTipo = document.getElementById("doador_tipo").value;
        var pfForm = document.getElementById("doacaoPF-fields");
        var pjForm = document.getElementById("doacaoPJ-fields");
        
        if (doadorTipo === "Físico") {
            pfForm.style.display = "block";
            pjForm.style.display = "none";
        } else if (doadorTipo === "Jurídico") {
            pfForm.style.display = "none";
            pjForm.style.display = "block";
        } else {
            pfForm.style.display = "none";
            pjForm.style.display = "none";
        }
    }

    function toggleDoadorFields() {
    var tipoDoador = document.getElementById("tipo_doador").value;
    var cpfField = document.getElementById("cpf_field");
    var cnpjField = document.getElementById("cnpj_field");

    if (tipoDoador === "Físico") {
        cpfField.style.display = "block";
        cnpjField.style.display = "none";
    } else if (tipoDoador === "Jurídico") {
        cnpjField.style.display = "block";
        cpfField.style.display = "none";
    } else {
        cpfField.style.display = "none";
        cnpjField.style.display = "none";
    }
}

function formatarCPF(input) {
    let cpf = input.value.replace(/\D/g, '');

    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    input.value = cpf;
}

function formatarCNPJ(input) {
    let cnpj = input.value.replace(/\D/g, '');

    cnpj = cnpj.replace(/^(\d{2})(\d)/, '$1.$2');
    cnpj = cnpj.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
    cnpj = cnpj.replace(/\.(\d{3})(\d)/, '.$1/$2');
    cnpj = cnpj.replace(/(\d{4})(\d)/, '$1-$2');
    input.value = cnpj;
}

document.getElementById('entity').addEventListener('change', function() {
    var entityIdInput = document.getElementById('id');
    entityIdInput.value = '';
if (this.value === 'individuo') {
        entityIdInput.placeholder = "Digite o CPF";
        entityIdInput.oninput = function() {
            formatarCPF(this);
        };
    }else if (this.value === 'empresa') {
        entityIdInput.placeholder = "Digite o CNPJ";
        entityIdInput.oninput = function() {
            formatarCNPJ(this);
        };
    }
    else
        entityIdInput.placeholder = "";
});