resource "aws_ecr_repository" "foo" {
  name                 = "jan-summer-school-2023"
  image_tag_mutability = "MUTABLE"
}