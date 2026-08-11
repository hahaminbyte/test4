#!/usr/bin/env python3
"""
AI-Powered Commit History Generator
Analyzes project structure and generates realistic, contextual commit histories
"""

import os
import json
import random
import ast
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from pathlib import Path
import subprocess

class ProjectAnalyzer:
    """Deep project analysis for realistic commit generation"""
    
    def __init__(self, project_path: str, project_type: str, language: str):
        self.project_path = Path(project_path)
        self.project_type = project_type
        self.language = language
        self.file_structure = {}
        self.dependencies = []
        self.features = []
        self.complexity_score = 0
        
    def analyze_project_deeply(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis"""
        
        analysis = {
            "file_structure": self._analyze_file_structure(),
            "dependencies": self._analyze_dependencies(),
            "features": self._detect_features(),
            "complexity": self._calculate_complexity(),
            "architecture": self._detect_architecture_patterns(),
            "development_phases": self._generate_development_phases()
        }
        
        return analysis
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze file structure to understand project components"""
        
        structure = {
            "components": [],
            "tests": [],
            "configs": [],
            "documentation": [],
            "assets": []
        }
        
        # Scan project files
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.project_path))
                
                if self._is_source_file(file_path):
                    component = self._analyze_source_file(file_path)
                    structure["components"].append(component)
                elif self._is_test_file(file_path):
                    structure["tests"].append(relative_path)
                elif self._is_config_file(file_path):
                    structure["configs"].append(relative_path)
                elif self._is_documentation(file_path):
                    structure["documentation"].append(relative_path)
                elif self._is_asset_file(file_path):
                    structure["assets"].append(relative_path)
        
        return structure
    
    def _analyze_source_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual source file for functions, classes, etc."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            component = {
                "path": str(file_path.relative_to(self.project_path)),
                "functions": [],
                "classes": [],
                "imports": [],
                "complexity": 0,
                "size": len(content.split('\n'))
            }
            
            if self.language == "python":
                component.update(self._analyze_python_file(content))
            elif self.language in ["javascript", "typescript"]:
                component.update(self._analyze_js_ts_file(content))
            elif self.language == "java":
                component.update(self._analyze_java_file(content))
            
            return component
            
        except Exception:
            return {"path": str(file_path.relative_to(self.project_path)), "error": True}
    
    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "args": len(node.args.args),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "decorators": len(node.decorator_list)
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "inheritance": len(node.bases)
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or "relative")
            
            return {
                "functions": functions,
                "classes": classes,
                "imports": list(set(imports)),
                "complexity": len(functions) + len(classes) * 2
            }
            
        except:
            return {"functions": [], "classes": [], "imports": [], "complexity": 0}
    
    def _analyze_js_ts_file(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file"""
        
        # Simple regex-based analysis (could be enhanced with proper parser)
        functions = re.findall(r'(?:function\s+(\w+)|(\w+)\s*[=:]\s*(?:async\s+)?(?:\([^)]*\)\s*=>|function))', content)
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'(?:import|require)\s*.*?[\'"`]([^\'"`]+)[\'"`]', content)
        
        return {
            "functions": [{"name": f[0] or f[1]} for f in functions],
            "classes": [{"name": c} for c in classes],
            "imports": imports,
            "complexity": len(functions) + len(classes) * 2
        }
    
    def _analyze_java_file(self, content: str) -> Dict[str, Any]:
        """Analyze Java file"""
        
        classes = re.findall(r'(?:public\s+|private\s+|protected\s+)?class\s+(\w+)', content)
        methods = re.findall(r'(?:public|private|protected)\s+.*?\s+(\w+)\s*\([^)]*\)', content)
        imports = re.findall(r'import\s+([^;]+);', content)
        
        return {
            "functions": [{"name": m} for m in methods],
            "classes": [{"name": c} for c in classes],
            "imports": imports,
            "complexity": len(methods) + len(classes) * 2
        }
    
    def _analyze_dependencies(self) -> List[Dict[str, Any]]:
        """Analyze project dependencies"""
        
        dependencies = []
        
        # Check package.json
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    
                    for name, version in {**deps, **dev_deps}.items():
                        dependencies.append({
                            "name": name,
                            "version": version,
                            "type": self._categorize_dependency(name),
                            "is_dev": name in dev_deps
                        })
            except:
                pass
        
        # Check requirements.txt
        requirements = self.project_path / "requirements.txt"
        if requirements.exists():
            try:
                with open(requirements) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            name = line.split('==')[0].split('>=')[0].split('<=')[0]
                            dependencies.append({
                                "name": name,
                                "type": self._categorize_dependency(name),
                                "is_dev": False
                            })
            except:
                pass
        
        return dependencies
    
    def _categorize_dependency(self, name: str) -> str:
        """Categorize dependency by type"""
        
        web_frameworks = ["express", "fastapi", "flask", "django", "spring-boot", "react", "vue", "angular"]
        databases = ["mongodb", "postgresql", "mysql", "redis", "sqlite"]
        testing = ["jest", "pytest", "junit", "mocha", "chai", "cypress"]
        build_tools = ["webpack", "babel", "typescript", "eslint", "prettier"]
        auth = ["passport", "jsonwebtoken", "auth0", "oauth2"]
        
        name_lower = name.lower()
        
        if any(fw in name_lower for fw in web_frameworks):
            return "web_framework"
        elif any(db in name_lower for db in databases):
            return "database"
        elif any(test in name_lower for test in testing):
            return "testing"
        elif any(build in name_lower for build in build_tools):
            return "build_tools"
        elif any(auth in name_lower for auth in auth):
            return "authentication"
        else:
            return "utility"
    
    def _detect_features(self) -> List[Dict[str, Any]]:
        """Detect implemented features based on code analysis"""
        
        features = []
        
        # Analyze based on file patterns and code content
        feature_indicators = {
            "authentication": ["auth", "login", "jwt", "passport", "session"],
            "database": ["db", "model", "schema", "migration", "orm"],
            "api": ["router", "endpoint", "controller", "api", "rest"],
            "frontend": ["component", "view", "template", "ui", "page"],
            "testing": ["test", "spec", "mock", "fixture"],
            "security": ["security", "encrypt", "hash", "validate"],
            "performance": ["cache", "optimize", "lazy", "async"],
            "monitoring": ["log", "metric", "health", "monitor"]
        }
        
        for feature_name, keywords in feature_indicators.items():
            score = 0
            for component in self.file_structure.get("components", []):
                path = component.get("path", "").lower()
                if any(keyword in path for keyword in keywords):
                    score += 1
            
            if score > 0:
                features.append({
                    "name": feature_name,
                    "confidence": min(score / 3, 1.0),
                    "complexity": score
                })
        
        return features
    
    def _calculate_complexity(self) -> float:
        """Calculate overall project complexity"""
        
        total_files = len(self.file_structure.get("components", []))
        total_functions = sum(len(comp.get("functions", [])) for comp in self.file_structure.get("components", []))
        total_classes = sum(len(comp.get("classes", [])) for comp in self.file_structure.get("components", []))
        total_deps = len(self.dependencies)
        
        # Normalize complexity score
        complexity = (total_files * 0.1 + total_functions * 0.3 + total_classes * 0.5 + total_deps * 0.2) / 10
        
        return min(complexity, 1.0)
    
    def _detect_architecture_patterns(self) -> List[str]:
        """Detect architectural patterns used"""
        
        patterns = []
        
        # Check for common patterns
        file_paths = [comp.get("path", "") for comp in self.file_structure.get("components", [])]
        
        if any("controller" in path.lower() for path in file_paths):
            patterns.append("MVC")
        if any("service" in path.lower() for path in file_paths):
            patterns.append("Service Layer")
        if any("middleware" in path.lower() for path in file_paths):
            patterns.append("Middleware Pattern")
        if any("factory" in path.lower() for path in file_paths):
            patterns.append("Factory Pattern")
        if any("observer" in path.lower() for path in file_paths):
            patterns.append("Observer Pattern")
        
        return patterns
    
    def _generate_development_phases(self) -> List[Dict[str, Any]]:
        """Generate realistic development phases based on project analysis"""
        
        phases = [
            {
                "name": "Project Setup",
                "duration_days": random.randint(1, 3),
                "focus": ["initialization", "dependencies", "configuration"],
                "intensity": 0.3
            },
            {
                "name": "Core Development", 
                "duration_days": random.randint(14, 30),
                "focus": ["core_features", "business_logic", "api_development"],
                "intensity": 0.8
            },
            {
                "name": "Testing & Quality",
                "duration_days": random.randint(7, 14),
                "focus": ["testing", "bug_fixes", "code_review"],
                "intensity": 0.6
            },
            {
                "name": "Polish & Documentation",
                "duration_days": random.randint(3, 7),
                "focus": ["documentation", "refactoring", "performance"],
                "intensity": 0.4
            }
        ]
        
        # Adjust phases based on project complexity
        if self.complexity_score > 0.7:
            phases.append({
                "name": "Advanced Features",
                "duration_days": random.randint(10, 20),
                "focus": ["advanced_features", "integration", "optimization"],
                "intensity": 0.7
            })
        
        return phases
    
    def _is_source_file(self, path: Path) -> bool:
        """Check if file is a source code file"""
        source_extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "go": [".go"]
        }
        
        return path.suffix in source_extensions.get(self.language, [])
    
    def _is_test_file(self, path: Path) -> bool:
        """Check if file is a test file"""
        return any(pattern in str(path).lower() for pattern in ["test", "spec", "__test__"])
    
    def _is_config_file(self, path: Path) -> bool:
        """Check if file is a configuration file"""
        config_files = ["package.json", "requirements.txt", "tsconfig.json", "webpack.config.js", 
                       ".env", ".gitignore", "Dockerfile", "docker-compose.yml"]
        return path.name in config_files or path.suffix in [".json", ".yaml", ".yml", ".toml", ".ini"]
    
    def _is_documentation(self, path: Path) -> bool:
        """Check if file is documentation"""
        return path.suffix in [".md", ".rst", ".txt"] or "doc" in str(path).lower()
    
    def _is_asset_file(self, path: Path) -> bool:
        """Check if file is an asset"""
        return path.suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".scss", ".less"]


class AICommitGenerator:
    """AI-powered commit message and history generator"""
    
    def __init__(self, project_analysis: Dict[str, Any]):
        self.analysis = project_analysis
        self.commit_templates = self._load_intelligent_templates()
        
    def generate_realistic_commits(self, num_commits: int, days_back: int, developers: List[Dict]) -> List[Dict[str, Any]]:
        """Generate contextually realistic commits"""
        
        commits = []
        phases = self.analysis["development_phases"]
        
        # Calculate phase distribution
        total_days = sum(phase["duration_days"] for phase in phases)
        phase_commits = self._distribute_commits_across_phases(num_commits, phases)
        
        current_date = datetime.now() - timedelta(days=days_back)
        
        for phase_idx, phase in enumerate(phases):
            phase_commit_count = phase_commits[phase_idx]
            
            for i in range(phase_commit_count):
                commit = self._generate_contextual_commit(
                    phase, 
                    i / phase_commit_count,
                    developers,
                    current_date
                )
                commits.append(commit)
                
                # Advance date realistically
                current_date += timedelta(
                    hours=random.uniform(2, 48),  # Realistic intervals
                    minutes=random.randint(0, 59)
                )
        
        return sorted(commits, key=lambda x: x["date"])
    
    def _load_intelligent_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load context-aware commit templates"""
        
        return {
            "initialization": {
                "feat": [
                    "feat: initialize {language} project with {framework}",
                    "feat: setup {project_type} project structure",
                    "feat: configure {build_tool} build pipeline",
                    "feat: add initial {language} configuration"
                ],
                "chore": [
                    "chore: setup development environment",
                    "chore: configure {dependency} for {feature}",
                    "chore: initialize git repository with .gitignore",
                    "chore: add {license} license and README"
                ]
            },
            "core_features": {
                "feat": [
                    "feat: implement {feature} with {technology}",
                    "feat: add {component} component with {functionality}",
                    "feat: create {api_endpoint} API endpoint",
                    "feat: integrate {service} service layer",
                    "feat: implement {auth_method} authentication",
                    "feat: add {database_operation} functionality"
                ],
                "refactor": [
                    "refactor: optimize {component} for better performance",
                    "refactor: extract {utility} utility functions",
                    "refactor: improve {module} code structure",
                    "refactor: consolidate {feature} logic"
                ]
            },
            "testing": {
                "test": [
                    "test: add unit tests for {component}",
                    "test: implement integration tests for {feature}",
                    "test: add {test_type} test coverage for {module}",
                    "test: create mock objects for {service}"
                ],
                "fix": [
                    "fix: resolve {issue_type} in {component}",
                    "fix: handle edge case in {function}",
                    "fix: correct {validation} validation logic",
                    "fix: address {performance_issue} performance issue"
                ]
            },
            "documentation": {
                "docs": [
                    "docs: add comprehensive API documentation",
                    "docs: update {component} usage examples",
                    "docs: create installation and setup guide",
                    "docs: document {feature} implementation",
                    "docs: add inline code comments for {module}"
                ]
            },
            "performance": {
                "perf": [
                    "perf: optimize {operation} performance",
                    "perf: implement caching for {data_source}",
                    "perf: reduce memory usage in {component}",
                    "perf: improve {algorithm} efficiency"
                ]
            }
        }
    
    def _distribute_commits_across_phases(self, total_commits: int, phases: List[Dict]) -> List[int]:
        """Distribute commits across development phases realistically"""
        
        phase_commits = []
        remaining_commits = total_commits
        
        for i, phase in enumerate(phases):
            if i == len(phases) - 1:  # Last phase gets remaining commits
                phase_commits.append(remaining_commits)
            else:
                # Distribute based on phase intensity and duration
                base_commits = int(total_commits * (phase["duration_days"] / sum(p["duration_days"] for p in phases)))
                intensity_multiplier = phase["intensity"]
                commits_for_phase = max(1, int(base_commits * intensity_multiplier))
                
                phase_commits.append(min(commits_for_phase, remaining_commits))
                remaining_commits -= commits_for_phase
        
        return phase_commits
    
    def _generate_contextual_commit(self, phase: Dict, progress: float, developers: List[Dict], base_date: datetime) -> Dict[str, Any]:
        """Generate a contextual commit for the current phase"""
        
        # Select appropriate developer based on phase and expertise
        developer = self._select_contextual_developer(phase, developers)
        
        # Generate realistic commit message
        commit_type, message = self._generate_contextual_message(phase, progress)
        
        # Calculate realistic timing
        commit_date = self._calculate_realistic_timing(base_date, developer, phase)
        
        # Generate realistic file changes
        files_changed = self._generate_realistic_file_changes(phase, commit_type, progress)
        
        return {
            "message": message,
            "author": developer,
            "date": commit_date,
            "type": commit_type,
            "files": files_changed,
            "phase": phase["name"]
        }
    
    def _select_contextual_developer(self, phase: Dict, developers: List[Dict]) -> Dict[str, str]:
        """Select developer based on phase requirements and expertise"""
        
        # Developer specialization mapping
        specializations = {
            "Project Setup": ["DevOps Engineer", "Senior Developer", "Tech Lead"],
            "Core Development": ["Full Stack Developer", "Backend Developer", "Frontend Developer"],
            "Testing & Quality": ["QA Engineer", "Test Engineer", "Senior Developer"],
            "Polish & Documentation": ["Technical Writer", "Developer", "Documentation Specialist"],
            "Advanced Features": ["Senior Developer", "Architect", "Specialist"]
        }
        
        phase_specialists = specializations.get(phase["name"], ["Developer"])
        
        # Find matching developers or default to any
        matching_devs = [dev for dev in developers if any(spec in dev.get("role", "") for spec in phase_specialists)]
        
        if matching_devs:
            # Weight selection by activity level
            weights = [{"high": 3, "medium": 2, "low": 1}.get(dev.get("activity_level", "medium"), 1) for dev in matching_devs]
            return random.choices(matching_devs, weights=weights)[0]
        else:
            return random.choice(developers)
    
    def _generate_contextual_message(self, phase: Dict, progress: float) -> Tuple[str, str]:
        """Generate contextual commit message based on phase and progress"""
        
        phase_focus = phase["focus"][0]  # Primary focus of the phase
        
        # Select commit type based on phase and progress
        if phase_focus in ["initialization", "configuration"]:
            commit_type = random.choices(["feat", "chore"], weights=[0.3, 0.7])[0]
        elif phase_focus in ["core_features", "business_logic"]:
            commit_type = random.choices(["feat", "refactor", "fix"], weights=[0.6, 0.3, 0.1])[0]
        elif phase_focus in ["testing", "bug_fixes"]:
            commit_type = random.choices(["test", "fix", "refactor"], weights=[0.5, 0.4, 0.1])[0]
        elif phase_focus == "documentation":
            commit_type = random.choices(["docs", "feat"], weights=[0.8, 0.2])[0]
        else:
            commit_type = random.choices(["feat", "fix", "refactor", "docs"], weights=[0.4, 0.3, 0.2, 0.1])[0]
        
        # Get appropriate template
        templates = self.commit_templates.get(phase_focus, {}).get(commit_type, 
                   self.commit_templates["core_features"][commit_type])
        
        template = random.choice(templates)
        
        # Fill template with contextual information
        message = self._fill_commit_template(template, phase, progress)
        
        return commit_type, message
    
    def _fill_commit_template(self, template: str, phase: Dict, progress: float) -> str:
        """Fill commit template with contextual information"""
        
        # Extract project context
        features = [f["name"] for f in self.analysis["features"]]
        dependencies = [d["name"] for d in self.analysis["dependencies"]]
        components = [comp["path"].split("/")[-1].replace(".py", "").replace(".js", "").replace(".ts", "") 
                     for comp in self.analysis["file_structure"]["components"]]
        
        # Contextual replacements
        replacements = {
            "feature": random.choice(features) if features else "user management",
            "component": random.choice(components) if components else "core module", 
            "technology": random.choice(dependencies) if dependencies else "REST API",
            "framework": random.choice([d for d in dependencies if d in ["express", "react", "django", "spring"]]) or "framework",
            "language": self.analysis.get("language", "JavaScript"),
            "project_type": self.analysis.get("project_type", "application"),
            "dependency": random.choice(dependencies) if dependencies else "library",
            "service": random.choice(["authentication", "database", "notification", "payment"]),
            "api_endpoint": random.choice(["/users", "/auth", "/data", "/admin", "/api/v1"]),
            "functionality": random.choice(["validation", "processing", "rendering", "computation"]),
            "module": random.choice(components) if components else "core",
            "issue_type": random.choice(["null pointer exception", "validation error", "timeout issue", "memory leak"]),
            "performance_issue": random.choice(["slow query", "memory usage", "high CPU", "network latency"])
        }
        
        # Apply replacements
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def _calculate_realistic_timing(self, base_date: datetime, developer: Dict, phase: Dict) -> datetime:
        """Calculate realistic commit timing"""
        
        # Developer working patterns
        working_patterns = {
            "high": {"daily_commits": (2, 8), "work_hours": (8, 20), "weekend_prob": 0.3},
            "medium": {"daily_commits": (1, 4), "work_hours": (9, 18), "weekend_prob": 0.1}, 
            "low": {"daily_commits": (0, 2), "work_hours": (9, 17), "weekend_prob": 0.05}
        }
        
        activity_level = developer.get("activity_level", "medium")
        pattern = working_patterns[activity_level]
        
        # Adjust for phase intensity
        phase_intensity = phase["intensity"]
        
        # Calculate timing
        if base_date.weekday() >= 5:  # Weekend
            if random.random() > pattern["weekend_prob"] * phase_intensity:
                # Skip weekend, move to Monday
                days_to_monday = 7 - base_date.weekday()
                base_date += timedelta(days=days_to_monday)
        
        # Work hours with some variation
        work_start, work_end = pattern["work_hours"]
        hour = random.randint(work_start, work_end)
        
        # Add some realistic clustering (developers often commit in bursts)
        if random.random() < 0.3:  # 30% chance of clustering
            hour += random.randint(-2, 2)  # Cluster within 2 hours
            hour = max(work_start, min(work_end, hour))
        
        return base_date.replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
    
    def _generate_realistic_file_changes(self, phase: Dict, commit_type: str, progress: float) -> List[str]:
        """Generate realistic file changes for the commit"""
        
        components = self.analysis["file_structure"]["components"]
        
        if commit_type == "feat":
            # Feature commits typically affect multiple files
            num_files = random.randint(2, 5)
            return random.sample([comp["path"] for comp in components], min(num_files, len(components)))
        elif commit_type == "fix":
            # Bug fixes usually affect 1-2 files
            num_files = random.randint(1, 2)
            return random.sample([comp["path"] for comp in components], min(num_files, len(components)))
        elif commit_type == "test":
            # Test commits affect test files
            test_files = self.analysis["file_structure"]["tests"]
            return random.sample(test_files, min(random.randint(1, 3), len(test_files))) if test_files else ["tests/new_test.py"]
        elif commit_type == "docs":
            # Documentation commits
            doc_files = self.analysis["file_structure"]["documentation"]
            return doc_files[:random.randint(1, 2)] if doc_files else ["README.md"]
        else:
            # Default: 1-3 files
            num_files = random.randint(1, 3)
            return random.sample([comp["path"] for comp in components], min(num_files, len(components)))


def generate_ai_powered_commits(project_path: str, project_type: str, language: str, 
                               num_commits: int, days_back: int, developers: List[Dict]) -> List[Dict[str, Any]]:
    """Main function to generate AI-powered commit history"""
    
    # Analyze project deeply
    analyzer = ProjectAnalyzer(project_path, project_type, language)
    analysis = analyzer.analyze_project_deeply()
    
    # Generate contextual commits
    generator = AICommitGenerator(analysis)
    commits = generator.generate_realistic_commits(num_commits, days_back, developers)
    
    return commits, analysis


if __name__ == "__main__":
    # Example usage
    developers = [
        {"name": "Alex Rivera", "email": "alex.rivera@codepulse.dev", "role": "Senior Full Stack Developer", "activity_level": "high"},
        {"name": "Sarah Chen", "email": "sarah.chen@codepulse.dev", "role": "DevOps Engineer", "activity_level": "medium"}
    ]
    
    commits, analysis = generate_ai_powered_commits(
        project_path="./test_project",
        project_type="web_app", 
        language="typescript",
        num_commits=50,
        days_back=90,
        developers=developers
    )
    
    print(f"Generated {len(commits)} contextual commits")
    print(f"Project complexity: {analysis['complexity']:.2f}")
    print("Development phases:", [phase["name"] for phase in analysis["development_phases"]])

# PR: Improve core module reliability
# Contextual improvement from pull request history
