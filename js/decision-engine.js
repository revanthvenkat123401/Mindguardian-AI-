/**
 * Decision Engine - Generates interventions and recommendations
 * Combines LLM outputs with rule-based logic for robust decision making
 */

class DecisionEngine {
    constructor(llmEngine) {
        this.llmEngine = llmEngine;
        this.interventionHistory = [];
        this.decisionLog = [];
        this.currentDecision = null;
        this.rules = this.initializeRules();
    }

    initializeRules() {
        return {
            burnoutRisk: [
                { threshold: 80, action: 'CRITICAL_INTERVENTION', priority: 'URGENT' },
                { threshold: 60, action: 'STRONG_INTERVENTION', priority: 'HIGH' },
                { threshold: 40, action: 'MILD_INTERVENTION', priority: 'MEDIUM' },
                { threshold: 0, action: 'MONITOR', priority: 'LOW' }
            ],
            stressLevel: [
                { threshold: 80, action: 'STRESS_RELIEF', priority: 'HIGH' },
                { threshold: 50, action: 'STRESS_AWARENESS', priority: 'MEDIUM' },
                { threshold: 0, action: 'MAINTAIN', priority: 'LOW' }
            ],
            fatigue: [
                { threshold: 80, action: 'ENERGY_BOOST', priority: 'HIGH' },
                { threshold: 50, action: 'REST_SUGGESTED', priority: 'MEDIUM' },
                { threshold: 0, action: 'MAINTAIN', priority: 'LOW' }
            ]
        };
    }

    async makeDecision(fusedFeatures, sessionContext = {}) {
        // Get LLM recommendation
        const llmDecision = await this.llmEngine.generateDecision(fusedFeatures, sessionContext);
        
        // Apply rule-based logic
        const ruleDecision = this.applyRules(fusedFeatures);
        
        // Merge decisions
        const finalDecision = this.mergeDecisions(llmDecision, ruleDecision, fusedFeatures);
        
        // Store in history
        this.currentDecision = finalDecision;
        this.decisionLog.push(finalDecision);
        
        return finalDecision;
    }

    applyRules(fusedFeatures) {
        const decisions = [];
        
        // Check burnout risk rules
        const burnoutRule = this.checkThreshold(this.rules.burnoutRisk, fusedFeatures.burnoutRisk);
        decisions.push(burnoutRule);
        
        // Check stress rules
        const stressRule = this.checkThreshold(this.rules.stressLevel, fusedFeatures.stressLevel);
        decisions.push(stressRule);
        
        // Check fatigue rules
        const fatigueRule = this.checkThreshold(this.rules.fatigue, fusedFeatures.fatigue);
        decisions.push(fatigueRule);
        
        return decisions;
    }

    checkThreshold(rules, value) {
        for (let rule of rules) {
            if (value >= rule.threshold) {
                return rule;
            }
        }
        return rules[rules.length - 1];
    }

    mergeDecisions(llmDecision, ruleDecisions, fusedFeatures) {
        const highestPriority = this.getHighestPriority(ruleDecisions);
        const riskCategory = this.getRiskCategory(fusedFeatures.burnoutRisk);
        
        return {
            id: Date.now(),
            timestamp: Date.now(),
            state: this.determineState(fusedFeatures),
            priority: highestPriority,
            action: llmDecision.recommendation || 'Continue monitoring',
            reason: llmDecision.concern || 'Routine wellness check',
            riskCategory,
            burnoutRisk: fusedFeatures.burnoutRisk,
            stressLevel: fusedFeatures.stressLevel,
            fatigue: fusedFeatures.fatigue,
            engagement: fusedFeatures.engagement,
            confidence: llmDecision.confidence || 85,
            llmAssessment: llmDecision.assessment,
            recoveryTime: llmDecision.recoveryTime,
            metrics: {
                cognitive_load: Math.round(fusedFeatures.cognitiveLoad),
                stress: Math.round(fusedFeatures.stressLevel),
                fatigue: Math.round(fusedFeatures.fatigue),
                engagement: Math.round(fusedFeatures.engagement)
            }
        };
    }

    determineState(fusedFeatures) {
        if (fusedFeatures.burnoutRisk > 70) return 'CRITICAL';
        if (fusedFeatures.burnoutRisk > 50) return 'WARNING';
        if (fusedFeatures.burnoutRisk > 30) return 'ALERT';
        return 'HEALTHY';
    }

    getRiskCategory(riskScore) {
        if (riskScore < 30) return 'Low';
        if (riskScore < 60) return 'Medium';
        return 'High';
    }

    getHighestPriority(ruleDecisions) {
        const priorityOrder = { 'URGENT': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 };
        let highest = 'LOW';
        
        ruleDecisions.forEach(decision => {
            if (priorityOrder[decision.priority] > priorityOrder[highest]) {
                highest = decision.priority;
            }
        });
        
        return highest;
    }

    executeIntervention(decision) {
        // Log intervention
        this.interventionHistory.push({
            timestamp: Date.now(),
            action: decision.action,
            reason: decision.reason,
            state: decision.state
        });
        
        // Trigger intervention (would integrate with UI)
        console.log('[DecisionEngine] Intervention Executed:', decision.action);
        
        return {
            status: 'executed',
            intervention: decision.action,
            expectedRecovery: decision.recoveryTime
        };
    }

    getDecisionLog() {
        return this.decisionLog;
    }

    getInterventionHistory() {
        return this.interventionHistory;
    }

    getCurrentDecision() {
        return this.currentDecision;
    }
}
