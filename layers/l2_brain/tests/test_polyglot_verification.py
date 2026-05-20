from layers.l2_brain.governance.polyglot_verification import (
    VerificationResult,
    build_polyglot_verification_plan,
    evaluate_verification_results,
    parse_git_status_paths,
)


def test_polyglot_plan_requires_python_go_specs_and_aiwg_checks():
    plan = build_polyglot_verification_plan(
        [
            "layers/l2_brain/governance/truth_validator.py",
            "layers/l1_nervous/main.go",
            "doc/specs/109_polyglot_architecture_registry.md",
            ".aiwg/state/current_truth.json",
        ]
    )

    commands = [item.command for item in plan.required_commands]

    assert "uv run pytest -q layers/l2_brain/tests" in commands
    assert "cd layers/l1_nervous && go test ./..." in commands
    assert "python3 scripts/validate_specs_docs.py" in commands
    assert "PYTHONPATH=. uv run pytest -q layers/l2_brain/tests/test_aiwg_pack_guard.py" in commands
    assert "git diff --check" in commands
    assert plan.languages == ["go", "markdown", "python"]
    assert plan.layers == ["AIWG", "L1", "L2", "specs"]


def test_polyglot_plan_deduplicates_commands_and_ignores_generated_noise():
    plan = build_polyglot_verification_plan(
        [
            "layers/l2_brain/foo.py",
            "layers/l2_brain/bar.py",
            "layers/l2_brain/__pycache__/foo.cpython-314.pyc",
            "layers/l1_nervous/proto/core.pb.go",
        ]
    )

    commands = [item.command for item in plan.required_commands]

    assert commands.count("uv run pytest -q layers/l2_brain/tests") == 1
    assert "cd layers/l1_nervous && go test ./..." not in commands


def test_verification_results_block_push_when_required_command_fails():
    verdict = evaluate_verification_results(
        build_polyglot_verification_plan(["layers/l1_nervous/main.go"]),
        [
            VerificationResult(command="git diff --check", exit_code=0),
            VerificationResult(command="cd layers/l1_nervous && go test ./...", exit_code=1, stderr="build failed"),
        ],
    )

    assert not verdict.ready_to_commit
    assert not verdict.ready_to_push
    assert verdict.failed_commands == ["cd layers/l1_nervous && go test ./..."]
    assert "required verification failed" in verdict.reason


def test_verification_results_allow_push_only_when_all_required_commands_pass():
    plan = build_polyglot_verification_plan(["layers/l2_brain/governance/truth_validator.py"])
    results = [
        VerificationResult(command=item.command, exit_code=0)
        for item in plan.required_commands
    ]

    verdict = evaluate_verification_results(plan, results)

    assert verdict.ready_to_commit
    assert verdict.ready_to_push
    assert verdict.failed_commands == []


def test_git_status_parser_extracts_renamed_and_untracked_paths():
    paths = parse_git_status_paths(
        " M layers/l2_brain/foo.py\n"
        "R  layers/l1_nervous/old.go -> layers/l1_nervous/new.go\n"
        "?? doc/specs/new_contract.md\n"
    )

    assert paths == [
        "layers/l2_brain/foo.py",
        "layers/l1_nervous/new.go",
        "doc/specs/new_contract.md",
    ]
