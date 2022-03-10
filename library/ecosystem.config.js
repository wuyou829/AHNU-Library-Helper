module.exports = {
  apps : [{
    name   : "app1",
    args: "runserver 0.0.0.0:80 --insecure --noreload",
    script: "manage.py",
  }]
}
