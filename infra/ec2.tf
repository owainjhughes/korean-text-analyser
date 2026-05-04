data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["137112412989"] # Amazon

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_eip" "app" {
  domain = "vpc"
  tags = {
    Name = "${var.project_name}-eip"
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.app.id]
  iam_instance_profile        = aws_iam_instance_profile.instance.name
  associate_public_ip_address = true

  metadata_options {
    http_tokens                 = "required"
    http_endpoint               = "enabled"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    project_name  = var.project_name
    region        = local.region
    ecr_url       = local.ecr_url
    domain        = var.domain
    admin_email   = local.admin_email
    log_group     = aws_cloudwatch_log_group.app.name
    api_key_param = local.api_key_param
    pull_and_restart_body = templatefile("${path.module}/pull-and-restart.sh.tftpl", {
      region  = local.region
      ecr_url = local.ecr_url
    })
    caddyfile_body = templatefile("${path.module}/Caddyfile.tftpl", {
      domain      = var.domain
      admin_email = local.admin_email
    })
    systemd_unit_body = templatefile("${path.module}/korclass.service.tftpl", {
      region        = local.region
      ecr_url       = local.ecr_url
      log_group     = aws_cloudwatch_log_group.app.name
      api_key_param = local.api_key_param
    })
  })

  tags = {
    Name    = "${var.project_name}-app"
    Project = var.project_name
  }
}

resource "aws_eip_association" "app" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app.id
}
