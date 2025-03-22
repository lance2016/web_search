#!/usr/bin/env python3
"""
测试运行脚本
用法:
    python run_tests.py                  # 运行单元测试
    python run_tests.py --cov            # 运行单元测试并显示覆盖率
    python run_tests.py --integration    # 运行集成测试
    python run_tests.py --all            # 运行所有测试
"""

import os
import sys
import subprocess
import argparse


def setup_env_for_tests(integration=False):
    """设置测试环境变量"""
    test_env = os.environ.copy()
    
    if integration:
        # 集成测试使用.env.test中的实际API密钥
        test_env["APP_ENV"] = "testing"
        print("使用.env.test中的环境变量进行集成测试")
    else:
        # 单元测试使用模拟API密钥
        test_env["APP_ENV"] = "testing"
        test_env["GOOGLE_API_KEY"] = "test_api_key"
        test_env["GOOGLE_CSE_ID"] = "test_cse_id"
        
    return test_env


def run_tests(integration=False, show_coverage=False):
    """运行测试"""
    
    # 设置测试环境变量
    test_env = setup_env_for_tests(integration)
    
    # 构建pytest命令
    cmd = ["pytest", "-v"]
    
    # 确定测试文件
    if integration:
        cmd.append("app/tests/test_integration.py")
        print("运行集成测试...")
    else:
        # 排除集成测试
        cmd.extend(["app/tests", "--ignore=app/tests/test_integration.py"])
        print("运行单元测试...")
    
    # 如果需要显示覆盖率
    if show_coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
    
    # 运行测试
    result = subprocess.run(cmd, env=test_env)
    return result.returncode


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='运行测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--cov', action='store_true', help='显示代码覆盖率')
    
    args = parser.parse_args()
    
    if args.all:
        # 运行单元测试
        unit_exit_code = run_tests(integration=False, show_coverage=args.cov)
        print("\n" + "="*50 + "\n")
        # 运行集成测试
        integration_exit_code = run_tests(integration=True, show_coverage=args.cov)
        sys.exit(unit_exit_code or integration_exit_code)
    else:
        # 运行指定类型的测试
        exit_code = run_tests(integration=args.integration, show_coverage=args.cov)
        sys.exit(exit_code)


if __name__ == "__main__":
    main() 