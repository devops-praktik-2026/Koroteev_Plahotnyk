# Что описание отдаёт наружу после применения.
# Посмотреть: tofu output
#
# Главный смысл этого файла: отсюда адреса «серверов»
# будут сами попадать в список серверов для сценария настройки, и никто
# больше не будет вписывать их руками.

output "database_url" {
  description = "Готовая строка подключения к базе данных стенда"
  value       = "postgresql+psycopg://${var.db_user}:${var.db_password}@localhost:${var.db_port}/${var.db_name}"
  sensitive   = true
}

output "servers" {
  description = "Учебные «серверы»: имя, порт для входа и порт приложения"
  value = [
    for index, container in docker_container.server : {
      name     = container.name
      ssh_port = var.ssh_base_port + index
      app_port = var.app_base_port + index
    }
  ]
}

# ЗАДАНИЕ: добавьте вывод, из которого получается готовый
# список серверов для сценария настройки. Проверить можно так:
#
#     tofu output -raw ansible_inventory > ../ansible/inventory.ini
#     ansible-playbook -i ../ansible/inventory.ini ../ansible/site.yml
#
# output "ansible_inventory" {
#   value = <<-EOT
#     [app]
#     ...
#   EOT
# }
